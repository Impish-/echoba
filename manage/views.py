# -*- coding: utf-8 -*-
from toolz.base_classes import BaseHandler
from jinja2 import Environment, PackageLoader

env = Environment(loader=PackageLoader('manage', 'templates'))


class ManagePageView(BaseHandler):

    def get(self, *args, **kwargs):
        return env.get_template('manage.html').render()