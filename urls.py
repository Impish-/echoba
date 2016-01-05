from tornado import web
import os
from board.views import MainPageView
from manage.views import  LogOutHandler, ManageHandler, StaffManageHandler, EditStaffManageHandler, \
    DelStaffManagehandler

urls = [
    (r"/?$", MainPageView),

  #  (r"/([a-z]+)/$", BoardView),
  #  (r"/([a-z]+)/(\d)/$", ThreadView),

    (r"/manage/?", ManageHandler),
    (r"/manage/staff/?", StaffManageHandler),
    (r"/manage/staff/edit/(?P<username>\w+)?/?", EditStaffManageHandler),
    (r"/manage/staff/del/(?P<username>\w+)?/?", DelStaffManagehandler),

    (r"/logout", LogOutHandler),

  #  (r"/manage/board", ManageBoardView),

  #    (r"/ws", WebSocket),
    (r"/static/(.*)", web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "static")}),
]