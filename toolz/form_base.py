# -*- coding: utf-8 -*-
from wtforms_alchemy import model_form_factory

from wtforms_tornado import Form
from toolz.bd_toolz import with_session

ModelForm = model_form_factory(Form)


class FormCBV(ModelForm):
    session = None

    @classmethod
    @with_session
    def get_session(cls, session):
        if cls.session:
            return cls.session
        return session

    @classmethod
    def append_field(cls, name, field):
        setattr(cls, name, field)
        return cls