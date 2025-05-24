from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QListWidget, QLabel, QStackedWidget
from PyQt6.QtCore import Qt
from ui.pages.dashboard import DashboardPage
from ui.pages.new_post import NewPostPage
from ui.pages.history import HistoryPage
from ui.pages.settings import SettingsPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MultiPoster')
        self.setGeometry(100, 100, 1200, 800)
        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QHBoxLayout(self.central)

        # Боковое меню
        self.menu = QListWidget()
        self.menu.addItems(['Dashboard', 'New Post', 'History', 'Settings'])
        self.menu.setFixedWidth(180)
        self.menu.currentRowChanged.connect(self.switch_page)
        self.layout.addWidget(self.menu)

        # Страницы
        self.pages = QStackedWidget()
        self.dashboard = DashboardPage()
        self.new_post = NewPostPage()
        self.history = HistoryPage()
        self.settings = SettingsPage()
        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.new_post)
        self.pages.addWidget(self.history)
        self.pages.addWidget(self.settings)
        self.layout.addWidget(self.pages)

        self.menu.setCurrentRow(0)

    def switch_page(self, index):
        self.pages.setCurrentIndex(index) 