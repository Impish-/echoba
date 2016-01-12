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

import os, sys
from sqlalchemy_imageattach.stores.fs import HttpExposedFileSystemStore


SITE_ROOT = os.path.dirname(os.path.realpath(__file__))

store = HttpExposedFileSystemStore(
            path= '%s/media/' % SITE_ROOT ,
            prefix='static/images/'
        )

