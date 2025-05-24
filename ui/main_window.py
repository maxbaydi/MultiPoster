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
        self.menu.setFixedWidth(200)
        self.menu.currentRowChanged.connect(self.switch_page)
        self.layout.addWidget(self.menu)

        # Основная панель
        self.pages = QStackedWidget()
        self.dashboard = DashboardPage()
        self.new_post = NewPostPage()
        self.history = HistoryPage()
        self.settings = SettingsPage()
        self.pages.addWidget(self.dashboard)
        self.pages.addWidget(self.new_post)
        self.pages.addWidget(self.history)
        self.pages.addWidget(self.settings)
        self.pages.setStyleSheet('''
            QStackedWidget {
                background: #f4f6fa;
                border-radius: 12px;
            }
        ''')
        self.layout.addWidget(self.pages)

        # Глобальный стиль
        self.setStyleSheet('''
            /* Удалён QMainWindow { background: #181c22; } чтобы использовать системный светлый фон */
            QLabel {
                font-size: 20px;
                color: #23272e;
            }
            QPushButton {
                background: #00c3ff;
                color: #fff;
                border-radius: 8px;
                padding: 8px 20px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: #0099cc;
            }
            QLineEdit, QTextEdit, QComboBox, QSpinBox {
                background: #fff;
                border: 1px solid #cfd8dc;
                border-radius: 6px;
                padding: 6px;
                font-size: 16px;
            }
            QListWidget {
                background: #fff;
                color: #23272e;
                border: none;
                font-size: 18px;
                border-radius: 10px;
                padding: 8px 0 8px 0;
            }
            QListWidget::item {
                background: transparent;
                border: none;
                padding: 8px 16px;
                margin: 2px 0;
                border-radius: 6px;
            }
            QListWidget::item:selected {
                background: #00c3ff;
                color: #fff;
                border-left: 4px solid #0099cc;
            }
        ''')

        self.menu.setCurrentRow(0)

    def switch_page(self, index):
        self.pages.setCurrentIndex(index)