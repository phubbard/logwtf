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
    html_header = """
    <html>
    <title>logwtf REST server</title>
    <body>
    Welcome to <a href="https://github.com/phubbard/logwtf">logwtf</a>.
    <p>
    """
    html_footer = """
    </body>
    </html>
    """

    def __init__(self, data_object, name):
        resource.Resource.__init__(self)
        self.ilo = data_object
        self.name = name

    def render_GET(self, request):
        """
        Write a logfile to the client. Ignores the request and pulls relative
        url from self.name.
        @todo Use children classes for configuration and logfile transfer, not if/then/else
        """
        if self.name == 'favicon.ico':
            return ''

        try:
            format = request.args.get('format')[0]
        except:
            format = None

        logging.info('Got request for "%s"' % self.name)

        if self.name == '':
            # Force reload and parse on root page load
            self.ilo.load_and_parse()
            keys = self.ilo.get_names()
            request.write(self.html_header)
            request.write('<h3>Current logfile</h3>')
            request.write('<pre>%s</pre>' % self.ilo.fn)
            request.write('<a href="/get_configuration">Configuration</a><p>')
            request.write('Logs by identifier:<nl>')
            for x in keys:
                request.write('<li><a href="/%s?&format=text">%s</a>' % (x,x))
                request.write(' <a href="/%s">(json)</a></li>' % x)
            request.write('</nl>')
            request.write(self.html_footer)
            return ''

        if self.name == 'get_configuration':
            return json.dumps(self.ilo.get_config())

        # Normal log page
        if format == None:
           return(json.dumps(self.ilo.get_single_log(self.name)))
        else:
            request.write('<pre>')
            request.write(str(self.ilo.get_single_log(self.name)))
            request.write('</pre>')
            return ''

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
