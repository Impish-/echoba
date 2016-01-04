from jinja2 import Environment, PackageLoader
from tornado.web import RequestHandler

from manage.models import Staff


class BaseHandler(RequestHandler):
    def get_current_user(self):
        username = self.get_secure_cookie("username")
        if not username:
            return None
        return Staff.get_user(username)

    def get_context(self):
        context = {
               'current_user': self.get_current_user(),
               }
        if self.application.settings['xsrf_cookies']:
            context['xsrf_form_html'] = self.xsrf_form_html()
        print(context)
        return context