# -*- coding: utf-8 -*-
from manage.models import Staff
import tornado
from jinja2 import Environment, PackageLoader
from toolz.base_cls import BaseHandler

environtment = Environment(loader=PackageLoader('manage', 'templates'))


class ManageHandler(BaseHandler):
    def get(self):
        self.write(environtment.get_template('manage.html').render(self.get_context()))

    def post(self):
        user = Staff.get_auth(username=self.get_argument("login"), password=self.get_argument('password'))
        self.set_secure_cookie("username", user.name)

        # if user.role.code == 'adm':
        #     self.redirect("/manage")
        #     return
        self.redirect("/manage")


class LogOutHandler(BaseHandler):
    def get(self, *args, **kwargs):
        if self.get_current_user():
            self.clear_cookie("username")
        self.redirect('/manage')


