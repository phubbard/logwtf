#!/usr/bin/env python

"""
@file ionlog.py
@author Paul Hubbard
@brief Class to load and parse ion logfiles (http://ooici.net/)
@date 11/29/10
"""

import logging
import re

ION_LOGFILEDIR = '/Users/hubbard/code/lcaarch/logs'
ION_LOGFILE = ION_LOGFILEDIR + '/' + 'ioncontainer.log'

class IonLog():
    re_str = '^(\d\d\d\d\-\d\d\-\d\d\s\d\d:\d\d:\d\d\.\d\d\d)\s\[(\S+)\s*:\s*\S+\]\s(INFO|DEBUG)\s*:(.+)$'

    def __init__(self, filename=None):
        assert(filename != None)
        self.fn = filename
        self.regex = re.compile(self.re_str, re.M)

    def load_and_parse(self):
        try:
            logging.debug('Opening %s' % self.fn)
            fh = open(self.fn)
            logging.debug('Reading and parsing')
            pdata = self.regex.findall(fh.read())
            logging.debug('Done')
        except:
            logging.exception('Error reading file')
            return None

        # Split array of matches into N arrays based on process/entity name

        return pdata


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)s [%(funcName)s] %(message)s')
    il = IonLog(ION_LOGFILE)
    logging.debug(il.load_and_parse())
