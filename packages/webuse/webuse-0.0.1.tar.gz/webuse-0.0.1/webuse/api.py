from functools import cached_property

from aiohttp import web
from PySide6 import QtCore, QtWidgets

routes = web.RouteTableDef()


class ApiWidget(QtWidgets.QWidget):
    goto_sig = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_server()
        self.html = ""

    def setup_server(self):
        self.app.add_routes([web.get("/goto", self.goto)])
        self.app.add_routes([web.get("/content", self.content)])

    @cached_property
    def app(self):
        return web.Application()

    async def goto(self, request):
        url = request.query.get("url")
        self.goto_sig.emit(url)
        return web.Response(text="done.")

    async def content(self, request):
        return web.Response(text=self.html)
