"""An example server using the CherryPy web framework."""
import os
import optparse

import cherrypy

import amfast
from amfast.remoting.channel import ChannelSet
from amfast.remoting.wsgi_channel import WsgiChannel
from amfast.remoting.pyamf_endpoint import PyAmfEndpoint

import utils

class App(object):
    """Base web app."""
    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect('/hello_world.html')

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
    rpc_channel = WsgiChannel('amf-channel', endpoint=PyAmfEndpoint())
    channel_set.mapChannel(rpc_channel)
    utils.setup_channel_set(channel_set)

    app = App()
    cherrypy.tree.graft(rpc_channel, '/amf')
    cherrypy.quickstart(app, '/', config=cp_options)

    print "Serving on %s:%s" % (options.domain, options.port)
    print "Press ctrl-c to halt."
