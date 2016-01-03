from tornado import web
import os
from board.views import MainPageView
from manage.views import ManagePageView

urls = [
    (r"/?$", MainPageView),
  #  (r"/([a-z]+)/$", BoardView),
  #  (r"/([a-z]+)/(\d)/$", ThreadView),
  #  (r"/login", LoginHandler),
  #  (r"/manage/?$", ManagePageView),
  #  (r"/manage/board", ManageBoardView),
  #  (r"/manage/staff", ManageStaffView),
 #    (r"/ws", WebSocket),
  #  (r"/static/(.*)", web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "static")}),
]