from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from config.env_manager import EnvManager

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.env = EnvManager()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(14)
        title = QLabel('<h2 style="color:#00c3ff;">Settings</h2>')
        title.setStyleSheet('font-size:28px; font-weight:600; margin-bottom:20px;')
        layout.addWidget(title)
        self.wp_url = QLineEdit(self.env.get('WP_URL', ''))
        self.wp_user = QLineEdit(self.env.get('WP_USERNAME', ''))
        self.wp_pass = QLineEdit(self.env.get('WP_APP_PASSWORD', ''))
        self.tg_token = QLineEdit(self.env.get('TELEGRAM_BOT_TOKEN', ''))
        self.tg_channel = QLineEdit(self.env.get('TELEGRAM_CHANNEL_ID', ''))
        self.gpt_key = QLineEdit(self.env.get('VSEGPT_API_KEY', ''))
        self.gpt_url = QLineEdit(self.env.get('VSEGPT_URL', ''))
        for widget, label in [
            (self.wp_url, 'WordPress URL:'),
            (self.wp_user, 'WordPress Username:'),
            (self.wp_pass, 'WordPress App Password:'),
            (self.tg_token, 'Telegram Bot Token:'),
            (self.tg_channel, 'Telegram Channel ID:'),
            (self.gpt_key, 'VseGPT API Key:'),
            (self.gpt_url, 'VseGPT URL:')
        ]:
            l = QLabel(label)
            l.setStyleSheet('font-size:16px; color:#23272e;')
            layout.addWidget(l)
            widget.setStyleSheet('font-size:16px;')
            layout.addWidget(widget)
        self.save_btn = QPushButton('Save Settings')
        self.save_btn.setStyleSheet('margin-top: 18px;')
        self.save_btn.clicked.connect(self.save)
        layout.addWidget(self.save_btn)

    def save(self):
        self.env.set('WP_URL', self.wp_url.text())
        self.env.set('WP_USERNAME', self.wp_user.text())
        self.env.set('WP_APP_PASSWORD', self.wp_pass.text())
        self.env.set('TELEGRAM_BOT_TOKEN', self.tg_token.text())
        self.env.set('TELEGRAM_CHANNEL_ID', self.tg_channel.text())
        self.env.set('VSEGPT_API_KEY', self.gpt_key.text())
        self.env.set('VSEGPT_URL', self.gpt_url.text())
        QMessageBox.information(self, 'Settings', 'Settings saved!')