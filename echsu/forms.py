# -*- coding: utf-8 -*-

from wtforms import RadioField, BooleanField, HiddenField, FormField, FileField, ValidationError
from wtforms_alchemy import model_form_factory, ModelFieldList
from wtforms_components import validators
from wtforms_tornado import Form

from manage.models import Thread, Message
from toolz.bd_toolz import with_session
from toolz.recaptcha import RecaptchaField, RecaptchaValidator

ModelForm = model_form_factory(Form)


class CreateThreadForm(ModelForm):
    class Meta:
        model = Thread
        exclude = ['bumped']

    @classmethod
    @with_session
    def get_session(cls,session):
        return session


class MessageForm(ModelForm):
    class Meta:
        model = Message
        exclude = ['ip_address', 'datetime']
    sage = BooleanField(u'Сажа',)
    image = FileField(u'Изображение')
    # captcha = RecaptchaField(u'Капча')

    def validate_image(self, field):
        if self.op_post:
            if not self.image_attached:
                self.image.errors = [u'Для создания треда, прицепи картинку',]
                return False

        if not self.image_attached and len(self.message.data) < 1:
            self.message.errors = [u'Тут ничего нет!',]
            raise ValueError(u'Пустое сообщение')
        return True



    @classmethod
    @with_session
    def get_session(cls, session):
        return session

