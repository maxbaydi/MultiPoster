from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QScrollArea, QComboBox
from config.settings_manager import SettingsManager
from api.wordpress_client import WordPressClient

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        # --- Добавляем скролл ---
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        layout = QVBoxLayout(content)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(14)
        title = QLabel('<h2 style="color:#00c3ff;">Settings</h2>')
        title.setStyleSheet('font-size:28px; font-weight:600; margin-bottom:20px;')
        layout.addWidget(title)

        # --- WordPress Sites ---
        self.wp_blocks = []
        self.wp_layout = QVBoxLayout()
        for site in self.settings.get_wordpress_sites():
            self.add_wp_block(site)
        self.add_wp_btn = QPushButton('+ Add WordPress Site')
        self.add_wp_btn.clicked.connect(self.add_wp_block)
        wp_title = QLabel('WordPress Sites:')
        wp_title.setStyleSheet('font-size:18px; margin-top:10px;')
        layout.addWidget(wp_title)
        layout.addLayout(self.wp_layout)
        layout.addWidget(self.add_wp_btn)

        # --- Telegram Bots ---
        self.tg_blocks = []
        self.tg_layout = QVBoxLayout()
        for bot in self.settings.get_telegram_bots():
            self.add_tg_block(bot)
        self.add_tg_btn = QPushButton('+ Add Telegram Bot')
        self.add_tg_btn.clicked.connect(self.add_tg_block)
        tg_title = QLabel('Telegram Bots:')
        tg_title.setStyleSheet('font-size:18px; margin-top:18px;')
        layout.addWidget(tg_title)
        layout.addLayout(self.tg_layout)
        layout.addWidget(self.add_tg_btn)

        # --- VseGPT ---
        vsegpt = self.settings.get_vsegpt()
        self.gpt_key = QLineEdit(vsegpt.get('api_key', ''))
        self.gpt_url = QLineEdit(vsegpt.get('url', ''))
        layout.addWidget(QLabel('VseGPT API Key:'))
        layout.addWidget(self.gpt_key)
        layout.addWidget(QLabel('VseGPT URL:'))
        layout.addWidget(self.gpt_url)

        self.save_btn = QPushButton('Save Settings')
        self.save_btn.setStyleSheet('margin-top: 18px;')
        self.save_btn.clicked.connect(self.save)
        layout.addWidget(self.save_btn)

        self.setFixedSize(1100, 800)
        scroll.setWidget(content)
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

    def add_wp_block(self, site=None):
        block = QVBoxLayout()
        row = QHBoxLayout()
        url_col = QVBoxLayout()
        url_label = QLabel('URL:')
        url_label.setStyleSheet('font-size:14px;')
        url = QLineEdit(site['url'] if site else '')
        url_col.addWidget(url_label)
        url_col.addWidget(url)
        user_col = QVBoxLayout()
        user_label = QLabel('User:')
        user_label.setStyleSheet('font-size:14px;')
        user = QLineEdit(site['username'] if site else '')
        user_col.addWidget(user_label)
        user_col.addWidget(user)
        pwd_col = QVBoxLayout()
        pwd_label = QLabel('Password:')
        pwd_label.setStyleSheet('font-size:14px;')
        pwd = QLineEdit(site['app_password'] if site else '')
        pwd_col.addWidget(pwd_label)
        pwd_col.addWidget(pwd)
        del_btn = QPushButton('-')
        def remove():
            for i, (b, url, user, pwd, cat_box, del_btn, url_label, user_label, pwd_label, cat_label) in enumerate(self.wp_blocks):
                if b == block:
                    for w in (url, user, pwd, cat_box, del_btn, url_label, user_label, pwd_label, cat_label):
                        w.deleteLater()
                    self.wp_layout.removeItem(b)
                    self.wp_blocks.pop(i)
                    break
        del_btn.clicked.connect(remove)
        row.addLayout(url_col)
        row.addLayout(user_col)
        row.addLayout(pwd_col)
        row.addWidget(del_btn)
        block.addLayout(row)
        # --- Категории ---
        cat_label = QLabel('Category:')
        cat_label.setStyleSheet('font-size:14px; margin-top:4px;')
        cat_box = QComboBox()
        cat_box.setMinimumWidth(180)
        cat_box.addItem('Loading...')
        if url.text() and user.text() and pwd.text():
            try:
                wp = WordPressClient(url.text(), user.text(), pwd.text())
                cats = wp.get_categories()
                cat_box.clear()
                for c in cats:
                    cat_box.addItem(f"{c['name']} ({c['slug']})", c['id'])
                if site and 'category_id' in site:
                    idx = cat_box.findData(site['category_id'])
                    if idx >= 0:
                        cat_box.setCurrentIndex(idx)
            except Exception:
                cat_box.clear()
                cat_box.addItem('Ошибка загрузки')
        block.addWidget(cat_label)
        block.addWidget(cat_box)
        self.wp_layout.addLayout(block)
        self.wp_blocks.append((block, url, user, pwd, cat_box, del_btn, url_label, user_label, pwd_label, cat_label))

    def add_tg_block(self, bot=None):
        block = QVBoxLayout()
        row = QHBoxLayout()
        token_col = QVBoxLayout()
        token_label = QLabel('Token:')
        token_label.setStyleSheet('font-size:14px;')
        token = QLineEdit(bot['token'] if bot else '')
        token_col.addWidget(token_label)
        token_col.addWidget(token)
        channel_col = QVBoxLayout()
        channel_label = QLabel('Channel:')
        channel_label.setStyleSheet('font-size:14px;')
        channel = QLineEdit(bot['channel_id'] if bot else '')
        channel_col.addWidget(channel_label)
        channel_col.addWidget(channel)
        del_btn = QPushButton('-')
        def remove():
            for i, (b, token, channel, del_btn, token_label, channel_label) in enumerate(self.tg_blocks):
                if b == block:
                    for w in (token, channel, del_btn, token_label, channel_label):
                        w.deleteLater()
                    self.tg_layout.removeItem(b)
                    self.tg_blocks.pop(i)
                    break
        del_btn.clicked.connect(remove)
        row.addLayout(token_col)
        row.addLayout(channel_col)
        row.addWidget(del_btn)
        block.addLayout(row)
        self.tg_layout.addLayout(block)
        self.tg_blocks.append((block, token, channel, del_btn, token_label, channel_label))

    def save(self):
        # WordPress
        sites = []
        for block in self.wp_blocks:
            # Исправлено: теперь распаковка по 10 элементам
            _, url, user, pwd, cat_box, del_btn, url_label, user_label, pwd_label, cat_label = block
            u, us, pw = url.text().strip(), user.text().strip(), pwd.text().strip()
            cat_id = cat_box.currentData() if cat_box.currentIndex() >= 0 else None
            if u and us and pw:
                site = {"url": u, "username": us, "app_password": pw}
                if cat_id:
                    site["category_id"] = cat_id
                sites.append(site)
        self.settings.set_wordpress_sites(sites)
        # Telegram
        bots = []
        for block in self.tg_blocks:
            _, token, channel, _, token_label, channel_label = block
            t, c = token.text().strip(), channel.text().strip()
            if t and c:
                bots.append({"token": t, "channel_id": c})
        self.settings.set_telegram_bots(bots)
        # VseGPT
        self.settings.set_vsegpt({
            "api_key": self.gpt_key.text().strip(),
            "url": self.gpt_url.text().strip()
        })
        QMessageBox.information(self, 'Settings', 'Settings saved!')