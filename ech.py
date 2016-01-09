#encoding: utf8

import argparse
import tornado
import tornado.web
import tornado.websocket
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop

import urls

settings = {
    'login_url': "/manage",
    'cookie_secret': "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    'xsrf_cookies': False,
}

application = tornado.web.Application(urls.urls, **settings)
application.webSocketsPool = []
application.password_salt = 'G98uasfjo9!j0p9kfdlkj-089'
application.media_dir = 'media'

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='its ech.su!')
    parser.add_argument('-p', '--port', type=int, dest='port', help='port')
    args = parser.parse_args()

    sockets = tornado.netutil.bind_sockets(args.port if args.port else 8888)
    tornado.process.fork_processes(0)

    server = HTTPServer(application)
    server.add_sockets(sockets)

    IOLoop.current().start()