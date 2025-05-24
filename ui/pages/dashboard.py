from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget
from db.db_manager import DBManager

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('<h2>Dashboard</h2>'))
        self.posts_list = QListWidget()
        layout.addWidget(self.posts_list)
        self.refresh_posts()

    def refresh_posts(self):
        db = DBManager()
        posts = db.get_posts()
        self.posts_list.clear()
        for post in posts[:10]:
            self.posts_list.addItem(f"{post[2]} | {post[6]} | {post[7]}") 