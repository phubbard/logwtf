#!/usr/bin/env python
"""
@file ws.py
@author Paul Hubbard
@date 11/22/10
@brief REST webserver for javascript log viewer
"""


from twisted.web import server, resource, client
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor

import simplejson as json
import logging
import uuid

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
    isLeaf = True
    """
    return log message X from file Y?
    """

    def __init__(self):
        resource.Resource.__init__(self)
        self.putChild("", self)

    def render_GET(self, request):
        logging.info('LFP got Got request %s' % str(request))
        page_gunk = str(uuid.uuid4())
        page = json.dumps(page_gunk)
        return page



def main():
    logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s %(levelname)s [%(funcName)s] %(message)s')
    root = resource.Resource()
    root.putChild('', RootPage())
    root.putChild('logs', LogFilePage())
    root.putChild('get_configuration', JsonConfigPage())
    site = server.Site(root)
    reactor.listenTCP(2200, site)
    logging.info('http://localhost:2200/')

if __name__ == '__main__':
    main()
    reactor.run()
