#encoding: utf8
import types
from jinja2 import Environment, PackageLoader
from torgen.edit import FormMixin as FormMixin_torgen
from tornado.web import RequestHandler

from manage.models import Staff, Board
from toolz.recaptcha import RecaptchaValidator


class FormMixin(FormMixin_torgen):
    form_context_name = None
    """
        Таки кошерный Form Mixin,
        Прилепляем формочку к любому Class Base Handler'у
        и наслаждаемся формочкой!
        хуй знает велосипед или нет,но в торгене:
            1)FormHandler - корявый
            2)Можно замешивать в любой(из проверенных) торгеновский Handler
    """
    def post(self, *args, **kwargs):
        super(FormMixin, self).post(*args, **kwargs)
        try:
            self.object = self.get_object()
        except AttributeError:
            self.object = None

        try:
            self.object_list = self.get_queryset()
        except AttributeError:
            pass

        form = self.form_class(self.request.arguments, obj=self.object)
        return self.form_valid(form) if form.validate() else self.form_invalid(form)

    def get_form_kwargs(self):
        kwargs = super(FormMixin, self).get_form_kwargs()
        try:
            kwargs['obj'] = obj=self.object
        except AttributeError:
            pass
        return kwargs

    def get_context_data(self, **kwargs):
        context = super(FormMixin, self).get_context_data(**kwargs)
        context[self.form_context_name if self.form_context_name else 'form'] = self.get_form(self.form_class)
        return context

    def form_valid(self, form):
        try:
            self.object = self.get_object()
        except AttributeError:
            self.object = self.model()
            self.db.add(self.object)

        form.populate_obj(self.object)
        self.db.commit()
        try:
            return self.redirect(self.get_success_url())
        except:
            pass

    def form_invalid(self, form):
        context_form = super(self.__class__, self).get_context_data(**self.kwargs if self.kwargs else {})
        context_form['form'] = form
        return self.render(context_form)


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

        kwargs.update({
            'board_list': self.db.query(Board).order_by(Board.dir).all()
        })

        kwargs['current_user'] = self.get_current_user()
        if self.application.settings['xsrf_cookies']:
            kwargs['xsrf_form_html'] = self.xsrf_form_html()
        return super(BaseMixin, self).get_context_data(**kwargs)


class HardCodeVarsMixin(object):
    def get_context_data(self, **kwargs):
        context = {}

        return context


class BoardDataMixin(BaseMixin) :
    """
    lll
    """
    pass

