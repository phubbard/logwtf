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

LOGFILEDIR = 'logfiles'

class JsonConfigPage(resource.Resource):
    isLeaf = True

    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild('', self)

    def render_GET(self, request):
        logging.debug('Got config request')
        cfg = {'num_cols' : 3,
               'column_names' : ['foo', 'bar', 'baz']}
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
        logging.info('LFP got Got request %s' % str(request))
        return self._xform_logfile(LOGFILEDIR + '/' + self.filename)

    def _xform_logfile(self, filename):
        """
        Take a logfile and return it as a json string of the form
        Array of 2-element tuples (timestamp (int), string)
        """
        logging.debug('starting xform of %s' % filename)
        m = []

        for line in fileinput.input(filename):
            ts, msg = line.split(':')
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
    logging.basicConfig(level=logging.DEBUG,
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
