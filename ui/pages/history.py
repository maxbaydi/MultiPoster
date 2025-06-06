from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox
from db.db_manager import DBManager

class HistoryPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(18)
        title = QLabel('<h2 style="color:#00c3ff;">History</h2>')
        title.setStyleSheet('font-size:28px; font-weight:600; margin-bottom:20px;')
        layout.addWidget(title)
        self.posts_list = QListWidget()
        self.posts_list.setStyleSheet('''
            QListWidget {
                background: #fff;
                border-radius: 10px;
                font-size: 16px;
                padding: 10px;
            }
        ''')
        layout.addWidget(self.posts_list)
        self.refresh_btn = QPushButton('Refresh')
        self.refresh_btn.setStyleSheet('margin-top: 10px;')
        self.refresh_btn.clicked.connect(self.refresh_posts)
        layout.addWidget(self.refresh_btn)
        self.refresh_posts()

    def refresh_posts(self):
        db = DBManager()
        posts = db.get_posts()
        self.posts_list.clear()
        for post in posts:
            self.posts_list.addItem(f"{post[2]} | {post[6]} | {post[7]}")