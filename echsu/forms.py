# -*- coding: utf-8 -*-

from wtforms import RadioField, BooleanField, HiddenField, FormField, FileField
from wtforms_alchemy import model_form_factory, ModelFieldList
from wtforms_components import validators
from wtforms_tornado import Form

from manage.models import Thread, Message
from toolz.bd_toolz import with_session

ModelForm = model_form_factory(Form)


class CreateThreadForm(ModelForm):
    class Meta:
        model = Thread

    #message = ModelFieldList(FormField(MessageForm))\
    @classmethod
    @with_session
    def get_session(cls,session):
        return session


class MessageForm(ModelForm):
    class Meta:
        model = Message
        exclude = ['ip_address']
    sage = BooleanField(u'Сажа',)
    image = FileField(u'Изображение')

    #thread = ModelFieldList(FormField(CreateThreadForm))
    @classmethod
    @with_session
    def get_session(cls,session):
        return session

