#encoding: utf8

import argparse
import tornado
import tornado.web
import tornado.websocket
from sqlalchemy.orm import scoped_session, sessionmaker
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

from settings import settings
from toolz.bd_toolz import get_engine

try:
    from settings import tornado_settings
except ImportError:
    from settings_local import tornado_settings

import urls

settings.update(tornado_settings)

application = tornado.web.Application(urls.urls, **settings)
application.webSocketsPool = []
application.db = scoped_session(sessionmaker(bind=get_engine()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='its ech.su!')
    parser.add_argument('-p', '--port', type=int, dest='port', help='port')
    args = parser.parse_args()

    server = HTTPServer(application)
    server.bind(args.port if args.port else 8888)
    server.start(0)  # Forks multiple sub-processes
    IOLoop.current().start()

    # sockets = tornado.netutil.bind_sockets()
    # tornado.process.fork_processes(0)
    #
    # server = HTTPServer(application)
    # server.add_sockets(sockets)
    #
    # IOLoop.current().start()