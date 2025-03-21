from PySide6.QtCore import QUrl, Slot
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .api import ApiWidget

# from qasync import asyncClose, asyncSlot


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.api = ApiWidget()
        self.api.setVisible(False)  # no need to show the API
        self.tab = QTabWidget()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(self.api)
        layout.addWidget(self.tab)
        for i in range(8):
            tab = RenderWidget()
            self.tab.addTab(tab, str(i))

        self.setLayout(layout)

        # self.api.goto_sig.connect(self.update_url)


class RenderWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.html = ""

        self.webview = QWebEngineView()
        self.webview.load(QUrl("https://abrahamjuliot.github.io/creepjs/"))

        self.goto_button = QPushButton("Go")
        self.back_button = QPushButton("<")
        self.forward_button = QPushButton(">")
        self.refresh_button = QPushButton("⟳")
        self.address_bar = QLineEdit()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        header = QHBoxLayout()
        header.setContentsMargins(5, 0, 5, 0)
        header.addWidget(self.back_button)
        header.addWidget(self.forward_button)
        header.addWidget(self.refresh_button)
        header.addWidget(self.address_bar)
        header.addWidget(self.goto_button)

        layout.addLayout(header)
        layout.addWidget(self.webview)

        self.setLayout(layout)

        # User action signals
        self.goto_button.clicked.connect(self.on_goto_clicked)
        self.back_button.clicked.connect(self.webview.back)
        self.forward_button.clicked.connect(self.webview.forward)
        self.refresh_button.clicked.connect(self.webview.reload)
        self.address_bar.returnPressed.connect(self.on_goto_clicked)

        # Page events
        self.webview.urlChanged.connect(self.on_url_changed)
        self.webview.loadFinished.connect(self.on_load_finished)

    @Slot()
    def on_goto_clicked(self):
        self.webview.page().profile().setHttpUserAgent("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")
        self.webview.load(QUrl(self.address_bar.text()))

    @Slot()
    def on_url_changed(self):
        self.address_bar.setText(self.webview.url().toString())

    @Slot()
    def on_load_finished(self, ok: bool):
        def assign(html):
            self.html = html

        self.webview.page().toHtml(assign)

    @Slot()
    def update_url(self, url):
        self.webview.load(QUrl(url))
