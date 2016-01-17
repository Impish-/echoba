# -*- coding: utf-8 -*-
from tornado import web
import os
from tornado.web import url

from echsu.views import MainPageView, ThreadView

from echsu.views import BoardView
from manage.views import  LogOutHandler, ManageHandler, StaffManageHandler, EditStaffManageHandler, \
    DelStaffManageHandler, AddBoardHandler

urls = [
    (r"/?$", MainPageView),

    (r"/manage/?", ManageHandler,),
    (r"/manage/staff/?", StaffManageHandler),
    (r"/manage/staff/edit/(?P<id>\w+)?/?", EditStaffManageHandler),
    (r"/manage/staff/del/(?P<id>\w+)?/?", DelStaffManageHandler),

    (r"/manage/board/add/?", AddBoardHandler),
    (r"/logout", LogOutHandler),

  #    (r"/ws", WebSocket),

    (r"/static/(.*)", web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "static")}),
    (r"/media/(.*)", web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "media")}),

    (r"/(?P<board_dir>[a-z]+)/?$", BoardView),
    (r"/(?P<board_dir>[a-z]+)/page_(?P<page>\d+)/?$", BoardView),
    (r"/(?P<board_dir>[a-z]+)/(?P<op_message_id>\d+)/?$", ThreadView),
]