#!/usr/bin/env python
"""
@file ws.py
@author Paul Hubbard
@date 11/22/10
@brief REST webserver for javascript log viewer
"""


from twisted.web import server, resource
from twisted.internet import reactor

import simplejson as json
import logging
import fileinput
import os
from stat import ST_MODE, S_ISREG

LOGFILEDIR = 'logfiles'

class JsonConfigPage(resource.Resource):
    isLeaf = True

    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild('', self)

    def render_GET(self, request):
        logging.info('Got config request, walking %s' % LOGFILEDIR)
        num_cols = 0
        column_names = []

        # @see file:///Users/hubbard/Documents/Python%202.6.5%20docs/library/stat.html
        for f in os.listdir(LOGFILEDIR):
            pathname = os.path.join(LOGFILEDIR, f)
            mode = os.stat(pathname)[ST_MODE]
            if S_ISREG(mode):
                # Regular file, add to list
                num_cols = num_cols + 1
                column_names.append(f)

        cfg = {'num_cols' : num_cols,
               'column_names' : column_names}
        logging.info('results of traversal: %s' % json.dumps(cfg))
        return json.dumps(cfg)

class RootPage(resource.Resource):
    isLeaf = True
    """
    Just return # of logfiles? Need to define API as REST.
    - Get # of logfiles
    - Get # of messages in a logfile
    - Get message X in file Y, returned as json with
      {timestamp, string}
      """

    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild("", self)

    def render_GET(self, request):
        logging.info('Got request %s' % str(request))
        return "1"

class LogFilePage(resource.Resource):
    """
    return log message X from file Y?
    """

    def __init__(self, logfile_name):
        resource.Resource.__init__(self)
        self.filename = logfile_name

    def render_GET(self, request):
        """
        Write a logfile to the client
        """
        logging.info('Got request for %s' % str(request))
        return self._xform_logfile(LOGFILEDIR + '/' + self.filename)

    def _xform_logfile(self, filename):
        """
        Take a logfile and return it as a json string of the form
        Array of 2-element array (timestamp, string)
        """
        logging.debug('starting xform of %s' % filename)
        m = []

        for line in fileinput.input(filename):
            ts, msg = line.strip().split(':')
            entry = list
            entry = [str(ts), str(msg)]
            m.append(entry)

        logging.debug('sending "%s"' % json.dumps(m))
        logging.debug('done with logfile %s'  % filename)
        return(json.dumps(m))

class LogFileRootPage(resource.Resource):
    """
    @see http://jcalderone.livejournal.com/48953.html
    """
    def getChild(self, name, request):
        return LogFilePage(name)


def main():
    logging.basicConfig(level=logging.INFO,
        format='%(asctime)s %(levelname)s [%(funcName)s] %(message)s')
    root = resource.Resource()
    root.putChild('', RootPage())
    root.putChild('logs', LogFileRootPage())
    root.putChild('get_configuration', JsonConfigPage())
    site = server.Site(root)
    reactor.listenTCP(2200, site)
    logging.info('http://localhost:2200/')

if __name__ == '__main__':
    main()
    reactor.run()
