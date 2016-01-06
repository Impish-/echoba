from jinja2 import Environment, PackageLoader
from tornado.web import RequestHandler

from manage.models import Staff


class BaseHandler(RequestHandler):
    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")
        if not user_id:
            return None
        return Staff.get_user_by_id(user_id)

    def get_context(self):
        context = {
               'current_user': self.get_current_user(),
               }
        if self.application.settings['xsrf_cookies']:
            context['xsrf_form_html'] = self.xsrf_form_html()
        return context