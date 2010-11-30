#!/usr/bin/env python
"""
@file ws.py
@author Paul Hubbard
@date 11/22/10
@brief REST webserver for javascript log viewer
"""


from twisted.web import server, resource
from twisted.web.server import Site
from twisted.internet import reactor

import simplejson as json
import logging
import fileinput
import os
import re
from stat import ST_MODE, S_ISREG

from ionlog import IonLog

ION_LOGFILEDIR = '/Users/hubbard/code/lcaarch/logs'
ION_LOGFILE = ION_LOGFILEDIR + '/' + 'ioncontainer.log'


class IonLFP(resource.Resource):
    def __init__(self, data_object, name):
        resource.Resource.__init__(self)
        self.ilo = data_object
        self.name = name

    def render_GET(self, request):
        """
        Write a logfile to the client. Ignores the request and pulls relative
        url from self.name.
        """
        if self.name == 'favicon.ico':
            return ''
        logging.info('Got request for "%s"' % self.name)

        if self.name == '':
            # Force reload and parse on root page???
            keys = self.ilo.get_names()
            request.write('<html>Logs by identifier:<nl>')
            for x in keys:
                request.write('<li><a href="/%s">%s</a></li>' % (x, x))
            request.write('</nl></html>')
            return ''

        if self.name == 'get_configuration':
            cfg = {'num_cols': len(self.ilo.get_names()),
                   'column_names': self.ilo.get_names()}
            return(json.dumps(cfg))

        # Normal log page
        return(json.dumps(self.ilo.get_single_log(self.name)))

class LogFileRootPage(resource.Resource):
    """
    @see http://jcalderone.livejournal.com/48953.html
    """
    def __init__(self, logfile_name):
        resource.Resource.__init__(self)
        self.fn = logfile_name
        self.ilo = IonLog(filename=logfile_name)

    def getChild(self, name, request):
        return IonLFP(self.ilo, name)


def main():
    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(levelname)s [%(funcName)s] %(message)s')
    root = LogFileRootPage(ION_LOGFILE)
    factory = Site(root)
    reactor.listenTCP(2200, factory)
    logging.info('http://localhost:2200/')

if __name__ == '__main__':
    main()
    reactor.run()
