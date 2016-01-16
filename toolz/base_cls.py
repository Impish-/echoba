#encoding: utf8
import types
from jinja2 import Environment, PackageLoader
from torgen.edit import FormMixin as FormMixin_torgen
from tornado.web import RequestHandler

from manage.models import Staff, Board
from toolz.recaptcha import RecaptchaValidator


class FormMixin(FormMixin_torgen):
    """
        Таки кошерный Form Mixin,
         Прилепляем формочку к любому Class Base Handler'у
         и наслаждаемся формочкой
    """
    def post(self, *args, **kwargs):
        super(FormMixin, self).post(*args, **kwargs)
        try:
            self.object = self.get_object()
        except AttributeError:
            self.object = None

        form = self.form_class(self.request.arguments, obj=self.object)
        return self.form_valid(form) if form.validate() else self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super(FormMixin, self).get_context_data(**kwargs)
        try:
            context['form'] = self.form_class(obj=self.object)
        except AttributeError:
            context['form'] = self.form_class()
        return context

    def form_valid(self, form):
        return self.render(self.get(**self.kwargs))


class FlashMixin(object):
    def get_flash(self, key='default'):
        message = self.get_secure_cookie('flash_' + key)
        if message is None:
            return ''
        self.clear_cookie('flash_' + key)
        return message.decode('UTF-8') if message else ''

    def set_flash(self, message, key='default'):
        tmp_mess = ''
        if type(message) is types.UnicodeType:
            tmp_mess = message.encode('UTF-8')
        else:
            tmp_mess = message
        self.set_secure_cookie('flash_' + key, tmp_mess)

    def has_flash(self, key='default'):
        return self.get_secure_cookie(key) is not None


class BaseMixin(object):
    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")
        if user_id:
            return self.db.query(Staff).get(user_id)
        else:
            return None

    def get_context_data(self, **kwargs):
        kwargs['current_user'] = self.get_current_user()
        if self.application.settings['xsrf_cookies']:
            kwargs['xsrf_form_html'] = self.xsrf_form_html()
        return super(BaseMixin, self).get_context_data(**kwargs)


class HardCodeVarsMixin(object):
    def get_context_data(self, **kwargs):
        return {
            'board_list': self.db.query(Board).all()
        }


class BoardDataMixin(BaseMixin, HardCodeVarsMixin):
    """
    lll
    """
    pass

