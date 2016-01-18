# -*- coding: utf-8 -*-
import json
import urllib
import urllib2
from wtforms import ValidationError
from wtforms.fields import Field

try:
    from settings import recaptcha_settings
except ImportError:
    from settings_local import recaptcha_settings


RECAPTCHA_ERROR_CODES = {
    'missing-input-secret': 'The secret parameter is missing.',
    'invalid-input-secret': 'The secret parameter is invalid or malformed.',
    'missing-input-response': 'The response parameter is missing.',
    'invalid-input-response': 'The response parameter is invalid or malformed.'
}


class RecaptchaWidget(object):
    '''
        Widget for reCaptcha field
    '''

    def __call__(self, field, error=None, **kwargs):
        self.public_key = u''
        return u'''
            <script src="https://www.google.com/recaptcha/api.js"></script>
            <div class="g-recaptcha" data-sitekey="%s"></div>
            ''' % (recaptcha_settings['public_key'],)


class RecaptchaValidator(object):
    '''
        Validates a reCaptcha
    '''

    def __init__(self, message=None, client_response = None):
        self.client_response = client_response
        if message is None:
            message = 'The response parameter is missing.'
        self.message = message

    def __call__(self, form, field):
        client_response = ''
        if self.client_response is not None:
            try:
                client_response = self.client_response[0]
            except IndexError:
                raise ValidationError(field.gettext(self.message))

        response = urllib2.urlopen('https://www.google.com/recaptcha/api/siteverify', urllib.urlencode({
            'secret': recaptcha_settings['private_key'],
            'response': client_response
        }))

        if response.code != 200:
            field.recaptcha_error = 'incorrect-captcha-sol'
            raise ValidationError(field.gettext(self.message))

        json_response = json.loads(response.read().decode('utf-8'))

        if json_response['success']:
            return True
        
        for error in json_response.get('error-codes', []):
            if error in RECAPTCHA_ERROR_CODES:
                raise ValidationError(RECAPTCHA_ERROR_CODES[error])

        field.recaptcha_error = 'incorrect-captcha-sol'
        raise ValidationError(field.gettext(self.message))


class RecaptchaField(Field):
    widget = RecaptchaWidget()
    recaptcha_error = None

    def process(self, formdata):
        """
            валидатор вешаем только в том случае.
             если поле 'g-recaptcha-response' обнаружено
        """
        try:
            self.validators = [RecaptchaValidator(client_response=formdata.getlist('g-recaptcha-response'))]
        except AttributeError:
            pass
        super(RecaptchaField, self).process(formdata)