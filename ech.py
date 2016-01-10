#encoding: utf8

import argparse
import tornado
import tornado.web
import tornado.websocket
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

try:
    from settings import tornado_settings
except ImportError:
    from settings_local import tornado_settings

import urls

application = tornado.web.Application(urls.urls, **tornado_settings)
application.webSocketsPool = []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='its ech.su!')
    parser.add_argument('-p', '--port', type=int, dest='port', help='port')
    args = parser.parse_args()

    sockets = tornado.netutil.bind_sockets(args.port if args.port else 8888)
    tornado.process.fork_processes(0)

    server = HTTPServer(application)
    server.add_sockets(sockets)

    IOLoop.current().start()