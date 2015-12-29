#encoding: utf8
import pymongo

# connection = pymongo.Connection('127.0.0.1', 27017)
# connection.ech.board.remove()

# TODO: Разбить на отдельные приложения, оформить файл settings
# TODO: Модератора/Администратора, какнибудь по другому оформить (в шаблоне)

import tornado.ioloop
import tornado.web
import tornado.websocket
import urls

settings = {
    'login_url': "/login",
    'cookie_secret': "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
    'xsrf_cookies': "True",
}

application = tornado.web.Application(urls.urls, **settings)
application.webSocketsPool = []
application.password_salt = 'G98uasfjo9!j0p9kfdlkj-089'
application.media_dir = 'media'

if __name__ == "__main__":
    application.listen(8000, address='127.0.0.1')
    tornado.ioloop.IOLoop.instance().start()