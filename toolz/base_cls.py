#encoding: utf8
from jinja2 import Environment, PackageLoader
from tornado.web import RequestHandler

from manage.models import Staff, Board


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

        #context precoosor nado?
        #TODO: подобие контекст процессорра (в каждом приложении?) чтобы таким хард-кодом не страдать
        context.update({'board_list': Board.get_all()})

        if self.application.settings['xsrf_cookies']:
            context['xsrf_form_html'] = self.xsrf_form_html()
        return context

    def get_flash(self, key='default'):
        message = self.get_secure_cookie('flash_' + key)
        if message is None:
            return ''
        self.clear_cookie('flash_' + key)
        return message if message else ''

    def set_flash(self, message, key='default'):
        self.set_secure_cookie('flash_' + key, message)

    def has_flash(self, key='default'):
        return self.get_secure_cookie(key) is not None

    def render_template(self, *args, **kwargs):
        context = self.get_context()
        context.update(**kwargs)
        self.write(self.template_env.get_template(self.template).render(context))
