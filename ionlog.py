#!/usr/bin/env python

"""
@file ionlog.py
@author Paul Hubbard
@brief Class to load and parse ion logfiles (http://ooici.net/)
@date 11/29/10
"""

import logging
import re
from datetime import datetime
from time import time

class IonLog():
    """
    IonLog is responsible for loading, parsing and rearranging the logs into a collection
    sorted by process name, and also for computing relative times.
    """

    """
    The Magic Regex (via komodo RX tool) to group up ion log messages into
    datetime, source/process/service, log level and message. e.g.

    ('2010-11-29 12:53:52.920',
     'service_process',
     'DEBUG',
     "Service-declare: {'version': '0.1.0', 'name': 'store', 'dependencies': []}")
    """
    re_str = '^(\d\d\d\d\-\d\d\-\d\d\s\d\d:\d\d:\d\d\.\d\d\d)\s\[(\S+)\s*:\s*\S+\]\s(INFO|DEBUG|ERROR|WARNING|CRITICAL|EXCEPTION)\s*:(.+)$'

    def __init__(self, filename=None):
        # Save logfile name for later, just init variables here.
        assert(filename != None)
        self.fn = filename
        # Note the multiline flag for the regex - will not work otherwise!
        self.regex = re.compile(self.re_str, re.M)
        self.max_delta_t = 0.0
        self.max_per_source = 0

    def _to_datetime(self, timestamp):
        """
        Convert from string into datetime.
        @see http://seehuhn.de/pages/pdate
        One-liner function to keep just one copy of the magic format string.
        """
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
        return dt

    def _delta_t(self, dtime_str):
        """
        Given a datetime string, compute delta in fractional seconds since tzero.
        """
        dtime = self._to_datetime(dtime_str)
        dt = dtime - self.tzero

        return(dt.seconds + (dt.days * 86400.0) + (dt.microseconds / 1000000.0))

    def _find_tzero(self):
        """
        Find starting logtime from logfile. Just reads the first line, parses it
        and pulls the timestamp.
        """
        logging.debug('looking for tzero...')
        try:
            fh = open(self.fn)
            line = fh.readline()
            fh.close()
            datum = self.regex.findall(line)
        except:
            logging.exception('Error looking for tzero!')
            return None

        dtime = self._to_datetime(datum[0][0])
        logging.debug('tzero is %s' % str(dtime))
        return dtime

    def _filter_character(self, char):
        """
        Filter out non-encodable characters, most common cases first for speed.
        """
        if char.isalnum():
            return True
        if char.isspace():
            return True
        if char in "[]{}\|;:'<>,./?`~!@#$%^&*()-_=+":
            return True
        return False

    def _filter_msg(self, mstr):
        """
        Some message strings are not json-encodable due to binary characters. This
        just removes anything non-alphanumeric or spaces. Filter is the fastest way
        to accomplish this.
        @see http://stackoverflow.com/questions/870520/in-python-how-do-you-filter-a-string-such-that-only-characters-in-your-list-are
        """
        return(filter(self._filter_character, mstr))

    def load_and_parse(self):
        """
        Trigger to load, parse and encode the datafile. Results available via
        get_keys and get_log.
        Call this to trigger a reload and reparse of the logfile.
        @retval None
        """
        tzero = time()
        try:
            logging.debug('Opening %s' % self.fn)
            fh = open(self.fn)
            logging.debug('Reading and parsing')
            pdata = self.regex.findall(fh.read())
            logging.debug('Done')
            fh.close()
            self.tzero = self._find_tzero()
        except:
            logging.exception('Error reading file')
            return None

        delta_t = time() - tzero
        logging.debug('Took %f seconds to find %d messages' % (delta_t, len(pdata)))
        # OK, we now have a list of tuples. Convert in two passes to N
        # arrays keyed on process/service name.

        tzero = time()
        # First, create array of arrays
        pdlist = {}
        # Next, walk and create an array for each unique process id
        for item in pdata:
            if not pdlist.has_key(item[1]):
                pdlist[item[1]] = []

        logging.debug('Found %d identities' % len(pdlist))
        # Now append the log messages to each array
        for item in pdata:
            dt = self._delta_t(item[0])
            # Keep track of max delta t and # of messages in a source
            if dt > self.max_delta_t:
                self.max_delta_t = dt
            val = {'time' : item[0],
                   'delta_t' : dt,
                   'level' : item[2],
                   'msg': self._filter_msg(item[3])}
            pdlist[item[1]].append(val)

        # Save data internally
        self.keys = pdlist.keys()
        self.data = pdlist

        # Compute source with max number of messages
        for key in pdlist.keys():
            if len(key) > self.max_per_source:
                self.max_per_source = len(key)

        delta_t = time() - tzero
        logging.debug('%f seconds to split data into arrays' % delta_t)
        logging.debug('Timespan: %f Max messages: %d' % (self.max_delta_t, self.max_per_source))

    def get_config(self):
        if not hasattr(self, 'keys'):
            logging.debug('Triggering loading and parsing')
            self.load_and_parse()
        cfg = {'num_cols' : len(self.get_names()),
               'column_names' : self.get_names(),
               'timespan': self.max_delta_t,
               'max_messages': self.max_per_source}
        return cfg

    def get_names(self):
        if not hasattr(self, 'keys'):
            logging.debug('Triggering loading and parsing')
            self.load_and_parse()

        return self.keys

    def get_single_log(self, ident_name):
        if not hasattr(self, 'keys'):
            logging.debug('Triggering loading and parsing')
            self.load_and_parse()

        return self.data[ident_name]
