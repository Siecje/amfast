"""An example server using the CherryPy web framework."""
import os
import optparse

import cherrypy

import amfast
from amfast.remoting.channel import ChannelSet
from amfast.remoting.cherrypy_channel import CherryPyChannel
from amfast.remoting.pyamf_endpoint import PyAmfEndpoint
import utils

class App(object):
    """Base web app."""
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect('/addressbook.html')

if __name__ == '__main__':
    usage = """usage: %s [options]""" % __file__
    parser = optparse.OptionParser(usage=usage)
    parser.add_option("-p", default=8000,
        dest="port", help="port number to serve")
    parser.add_option("-d", default="localhost",
        dest="domain", help="domain to serve")
    parser.add_option("-l", action="store_true",
        dest="log_debug", help="log debugging output")
    (options, args) = parser.parse_args()

    amfast.log_debug = options.log_debug

    cp_options = {
        'global':
        {
            'server.socket_port': int(options.port),
            'server.socket_host': str(options.domain),
        },
        '/':
        {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': os.path.join(os.getcwd(), '../flex/deploy')
        }
    }

    channel_set = ChannelSet()
    rpc_channel = CherryPyChannel('amf-channel')
    channel_set.mapChannel(rpc_channel)
    polling_channel = CherryPyChannel('amf-polling-channel')
    channel_set.mapChannel(polling_channel)
    utils.setup_channel_set(channel_set)

    # For testing PyAmf compatibility
    pyamf_channel = CherryPyChannel('pyamf-channel', endpoint=PyAmfEndpoint())
    channel_set.mapChannel(pyamf_channel)

    app = App()
    app.amf = rpc_channel.processMsg
    app.amfPolling = polling_channel.processMsg
    app.pyAmf = pyamf_channel.processMsg
    cherrypy.quickstart(app, '/', config=cp_options)

    print "Serving on %s:%s" % (options.domain, options.port)
    print "Press ctrl-c to halt."
