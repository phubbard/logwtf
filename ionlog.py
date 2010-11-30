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

class IonLog():
    """
    Magic regex (via komodo RX tool) to group up ion log messages into
    datetime, source/process/service, log level and message. e.g.

    ('2010-11-29 12:53:52.920',
     'service_process',
     'DEBUG',
     "Service-declare: {'version': '0.1.0', 'name': 'store', 'dependencies': []}")
    """
    re_str = '^(\d\d\d\d\-\d\d\-\d\d\s\d\d:\d\d:\d\d\.\d\d\d)\s\[(\S+)\s*:\s*\S+\]\s(INFO|DEBUG|ERROR|WARNING|CRITICAL|EXCEPTION)\s*:(.+)$'

    def __init__(self, filename=None):
        assert(filename != None)
        self.fn = filename
        # Note the multiline flag for the regex - will not work otherwise!
        self.regex = re.compile(self.re_str, re.M)

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

        logging.debug('Found %d messages in %s' % (len(pdata), self.fn))
        # OK, we now have a list of tuples. Convert in two passes to N
        # arrays keyed on process/service name.
        # First, create array of arrays
        pdlist = {}
        # Next, walk and create an array for each unique process id
        for item in pdata:
            if not pdlist.has_key(item[1]):
                pdlist[item[1]] = []

        logging.debug('Found %d identities' % len(pdlist))
        # Now append the log messages to each array
        for item in pdata:
            val = {'time' : item[0],
                   'delta_t' : self._delta_t(item[0]),
                   'level' : item[2],
                   'msg': self._filter_msg(item[3])}
            pdlist[item[1]].append(val)

        # Save data internally
        self.keys = pdlist.keys()
        self.data = pdlist

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
