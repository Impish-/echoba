# -*- coding: utf-8 -*-
from wtforms import BooleanField, validators, PasswordField, SelectField, StringField, SubmitField, ValidationError, \
    HiddenField
from wtforms.validators import InputRequired, EqualTo
from wtforms_tornado import Form

from manage.models import Staff


class StaffForm(Form):
    username = StringField(u'Юзернэйм', [validators.Length(min=4, max=25,
                                                           message=u'от 4 до 25 Символов!')])
    role = SelectField(u'Роль', choices=[('mod', 'Moderator'), ('adm', 'Admin')])


class StaffEditForm(StaffForm):
    password = PasswordField(u'Пароль', [EqualTo('confirm',
                                             message=u'Не совпадают ;(')
                                     ]
                         )
    confirm = PasswordField(u'Еще раз')

    id = HiddenField(label='')

    def validate_password(self, field):
        if field.data:
            if  len(field.data) not in range(6,25):
                raise ValidationError(u'от 6 до 25 Символов!')



class StaffAddForm(StaffForm):
    password = PasswordField(u'Пароль', [validators.Length(min=6, max=25,
                                                        message=u'от 6 до 25 Символов!'),
                                     InputRequired(message=u'Обязательно!'),
                                     EqualTo('confirm',
                                             message=u'Не совпадают ;(')
                                     ]
                         )
    confirm = PasswordField(u'Еще раз')

    def validate_username(form, field):
        if Staff.get_user(username=field.data):
            raise ValidationError(u'Юзернэйм занят!')