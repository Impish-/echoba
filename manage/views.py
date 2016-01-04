# -*- coding: utf-8 -*-
from manage.models import Staff
import tornado
from jinja2 import Environment, PackageLoader
from tornado.web import RequestHandler

env = Environment(loader=PackageLoader('manage', 'templates'))


class LoginHandler(RequestHandler):
    def get(self):
        self.write('<html><body><form action="/login" method="post">'
                   'Name: <input type="text" name="name">'
                   '<input type="submit" value="Sign in">'
                   '</form></body></html>')

    def post(self):
        self.set_secure_cookie("user", self.get_argument("name"))
        self.redirect("/")


@tornado.web.authenticated
class ManagePageView(RequestHandler):
    def get(self, *args, **kwargs):
        self.write(env.get_template('manage.html').render())


class ManageStaffView(RequestHandler):
    def get(self, *args, **kwargs):
        self.write(env.get_template('staff_list.html').render())
