# db = {
#         'driver': 'postgresql+psycopg2',
#         'bd_name': '',
#         'username': '',
#         'password': '',
#         'host': '',
#         'port': '',
#     }
#
# tornado_settings = {
#     'login_url': "/manage",
#     'cookie_secret': "",
#     'xsrf_cookies': False, # !!
#     'autoreload': False,
#     'debug': False,
#     'media': 'media',
#     'password_salt': '',
# }
#
# recaptcha_settings = {
#     'public_key': '',
#     'private_key': ''
# }

import os, sys
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from sqlalchemy_imageattach.stores.fs import  FileSystemStore
from tornado_jinja2 import Jinja2Loader

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))
STATIC_PATH = '%s/static/' % SITE_ROOT
MEDIA_PATH = '%s/media/' % SITE_ROOT

store = FileSystemStore(
            path=MEDIA_PATH,
            base_url='/media/'
        )

TEMPLATE_PATH = '%s/templates' % SITE_ROOT

jinja2_settings = {
            'autoescape': True,
            'extensions': [
                'jinja2.ext.with_'
            ],
        }

jinja2_environment = Environment(
            loader=FileSystemLoader(TEMPLATE_PATH),
            undefined=StrictUndefined,
            **jinja2_settings
        )

jinja2loader = Jinja2Loader(TEMPLATE_PATH)

settings = dict(
            template_path=TEMPLATE_PATH,
            static_path=STATIC_PATH,
            template_loader=jinja2loader
        )

# to settings_local
# email_settings = {
#     'from': 'Ech.su! <noreply@ech.su>',
#     'username': 'noreply@ech.su',
#     'password': '',
#     'smtp': 'smtp.yandex.ru:587'
# }


#bing_api_key = ''