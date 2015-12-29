from tornado import web

import os
urls = [
    (r"/?$", MainPage),
    (r"/([a-z]+)/$", BoardView),
    (r"/([a-z]+)/(\d)/$", ThreadView),
    (r"/login", LoginHandler),
    (r"/manage/board", ManageBoardView),
    (r"/manage/staff", ManageStaffView),
    (r"/ws", WebSocket),
    (r"/static/(.*)", web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), "static")}),
]