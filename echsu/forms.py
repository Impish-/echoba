# -*- coding: utf-8 -*-
import re
from wtforms import RadioField, BooleanField, HiddenField, FormField, FileField, ValidationError, PasswordField
from wtforms import validators
from wtforms.validators import InputRequired, EqualTo
from wtforms_alchemy import model_form_factory
from wtforms_components import  EmailField
from wtforms_tornado import Form

from manage.models import Thread, Message, Staff, Board
from toolz.form_base import FormCBV
from toolz.recaptcha import RecaptchaField, RecaptchaValidator

ModelForm = model_form_factory(Form)


class RegForm1(FormCBV):
    class Meta:
        model = Staff
        only = ['name']

    password = PasswordField(u'Пароль',
                             [validators.Length(min=6, max=25, message=u'от 6 до 25 Символов!'),
                              InputRequired(message=u'Обязательно!'),
                              EqualTo('confirm',
                                      message=u'Не совпадают ;(')
                              ]
                             )
    confirm = PasswordField(u'Еще раз')
    email = EmailField(u'E-mail', [InputRequired(message=u'Обязательно!'),])
    captcha = RecaptchaField(validators=[RecaptchaValidator()])


class RegBoard(FormCBV):
    class Meta:
        model = Board

    def validate_section_id(self, field):
        session = self.get_session()
        field.data = field.data if field.data > 0 else None
        if field.data is None:
            return
        if field.data not in [x.id for x in session.query(Section).options(load_only("id")).all()]:
            raise ValueError(u'Неверный раздел')

    def validate_available_from(self, field):
        time = re.match(r'(?P<hour>\d{1,2})\:(?P<min>\d{2})', field.data)
        if not time:
            raise ValidationError(u'Формат "ЧЧ:MM"')
        if int(time.group('hour')) not in range(0, 24):
            raise ValidationError(u'Неверное время! Формат "ЧЧ:ММ"')
        if int(time.group('min')) not in range(0, 60):
            raise ValidationError(u'Неверное время! Формат "ЧЧ:ММ"')

    def validate_available_until(self, field):
        time = re.match(r'(?P<hour>\d{1,2})\:(?P<min>\d{2})', field.data)
        if not time:
            raise ValidationError(u'Формат "ЧЧ:MM"')
        if int(time.group('hour')) not in range(0, 24):
            raise ValidationError(u'Неверное время! Формат "ЧЧ:ММ"')
        if int(time.group('min')) not in range(0, 60):
            raise ValidationError(u'Неверное время! Формат "ЧЧ:ММ"')


class CreateThreadForm(FormCBV):
    class Meta:
        model = Thread
        exclude = ['bumped']


class MessageForm(FormCBV):
    image_attached = False

    class Meta:
        model = Message
        exclude = ['ip_address', 'datetime', 'id']
    sage = BooleanField(u'Сажа',)
    image = FileField(u'Изображение')
    picrandom = BooleanField(u'Случайное изображение',)

    def validate_message(self, field):
        print len(field.data.replace(' ',''))
        if len(field.data.replace(' ','')) < 3:
             raise ValueError(u'Пустое сообщение')

    def validate_image(self, field):
        if self.op_post:
            if (not self.image_attached) and (not self.picrandom.data):
                self.image.errors = [u'Для создания треда, прицепи картинку',]
                return False
        if not (self.image_attached and self.picrandom) and len(self.message.data) < 1:
            self.message.errors = [u'Тут ничего нет!',]
            raise ValueError(u'Пустое сообщение')
        return True
