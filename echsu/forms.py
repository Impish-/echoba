# -*- coding: utf-8 -*-

from wtforms import RadioField, BooleanField, HiddenField, FormField, FileField, ValidationError
from wtforms_alchemy import model_form_factory, ModelFieldList
from wtforms_components import validators
from wtforms_tornado import Form

from manage.models import Thread, Message
from toolz.bd_toolz import with_session

ModelForm = model_form_factory(Form)


class CreateThreadForm(ModelForm):
    class Meta:
        model = Thread
        exclude = ['bumped']
    #message = ModelFieldList(FormField(MessageForm))\
    @classmethod
    @with_session
    def get_session(cls,session):
        return session


class MessageForm(ModelForm):
    class Meta:
        model = Message
        exclude = ['ip_address', 'datetime']

    op_post = False
    sage = BooleanField(u'Сажа',)
    image = FileField(u'Изображение')

    def validate(self):
        if self.op_post:
            if not self.image.data:
                self.image.errors = [u'Для создания треда, прицепи картинку',]
                return False
        if not self.image.data and not self.message.data:
            self.message.errors = [u'Тут ничего нет!',]
            return False
        return True


    #thread = ModelFieldList(FormField(CreateThreadForm))
    @classmethod
    @with_session
    def get_session(cls,session):
        return session

