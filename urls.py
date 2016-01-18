# -*- coding: utf-8 -*-
from tornado import web
import os
from tornado.web import URLSpec as url

from echsu.views import MainPageView, ThreadView

from echsu.views import BoardView
from manage.views import  LogOutHandler, ManageHandler, StaffManageHandler, EditStaffManageHandler, \
    DelStaffManageHandler, AddBoardHandler, DelMessageManageHandler, EditBoardHandler, MessageListHandler

urls = [
    url(r"/?$", MainPageView, name='main_page'),

    url(r"/manage/?", ManageHandler, name='manage'),
    url(r"/manage/staff/?", StaffManageHandler, name='staff_list'),
    url(r"/manage/staff/edit/(?P<id>\w+)?/?", EditStaffManageHandler, name='edit_staff'),
    url(r"/manage/staff/del/(?P<id>\w+)?/?", DelStaffManageHandler, name='delete_staff'),

    url(r'/manage/message/del/(?P<id>\d+)', DelMessageManageHandler, name='delete_message'),
    url(r'/manage/message/list/?$', MessageListHandler, name='message_list'),
    url(r'/manage/message/list/page=(?P<page>\d+)$', MessageListHandler, name='message_list_page'),

    url(r"/manage/board/add/?", AddBoardHandler, name='board_add'),
    url(r"/manage/board/edit/(?P<id>\w+)/?", EditBoardHandler, name='board_edit'),

    url(r"/logout", LogOutHandler, name='logout'),

  #    (r"/ws", WebSocket),

    url(r"/static/(.*)", web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "static")}),
    url(r"/media/(.*)", web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "media")}),

    url(r"/(?P<board_dir>[a-zA-Z1-9-]+)/?$", BoardView, name='board'),
    url(r"/(?P<board_dir>[a-zA-Z1-9-]+)/page=(?P<page>\d+)$", BoardView, name='board_page'),
    url(r"/(?P<board_dir>[a-zA-Z1-9-]+)/(?P<op_message_id>\d+)/?$", ThreadView, name='thread'),
]
