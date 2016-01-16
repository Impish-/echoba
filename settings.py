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
from sqlalchemy_imageattach.stores.fs import HttpExposedFileSystemStore, FileSystemStore

SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

store = FileSystemStore(
            path='%s/media/' % SITE_ROOT,
            base_url='/media/'
        )

