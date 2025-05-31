from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QTextEdit, QCheckBox, QSpinBox, QGroupBox,
                             QMessageBox, QComboBox, QSlider)
from PyQt6.QtCore import Qt
from config.settings_manager import SettingsManager

class TelegramSettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # Заголовок
        title = QLabel('<h2 style="color:#00c3ff;">Telegram Publishing Settings</h2>')
        title.setStyleSheet('font-size:28px; font-weight:600; margin-bottom:20px;')
        layout.addWidget(title)

        # Группа: Основные настройки
        main_group = QGroupBox("Основные настройки")
        main_layout = QVBoxLayout(main_group)
        
        # Включить/выключить публикацию в Telegram
        self.enable_telegram = QCheckBox('Включить публикацию в Telegram')
        self.enable_telegram.setChecked(True)
        main_layout.addWidget(self.enable_telegram)

        # Формат сообщения
        format_label = QLabel('Формат сообщения:')
        self.message_format = QComboBox()
        self.message_format.addItems(['Только текст', 'Текст + изображение', 'Только изображение с подписью'])
        main_layout.addWidget(format_label)
        main_layout.addWidget(self.message_format)

        layout.addWidget(main_group)

        # Группа: Настройки сообщения
        message_group = QGroupBox("Настройки сообщения")
        message_layout = QVBoxLayout(message_group)

        # Максимальная длина сообщения
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel('Максимальная длина сообщения:'))
        self.max_length = QSpinBox()
        self.max_length.setMinimum(100)
        self.max_length.setMaximum(4096)
        self.max_length.setValue(400)
        length_layout.addWidget(self.max_length)
        message_layout.addLayout(length_layout)

        # Префикс сообщения
        message_layout.addWidget(QLabel('Префикс сообщения:'))
        self.message_prefix = QLineEdit()
        self.message_prefix.setPlaceholderText('🔎 Quality. Warranty. Confidence.')
        message_layout.addWidget(self.message_prefix)

        # Суффикс сообщения
        message_layout.addWidget(QLabel('Суффикс сообщения:'))
        self.message_suffix = QLineEdit()
        self.message_suffix.setPlaceholderText('👉 See more at Global Vendor Network')
        message_layout.addWidget(self.message_suffix)

        # URL для ссылки
        message_layout.addWidget(QLabel('URL по умолчанию:'))
        self.default_url = QLineEdit()
        self.default_url.setPlaceholderText('https://gvn.biz/')
        message_layout.addWidget(self.default_url)

        layout.addWidget(message_group)

        # Группа: Настройки изображений
        image_group = QGroupBox("Настройки изображений")
        image_layout = QVBoxLayout(image_group)

        # Сжатие изображений
        self.compress_images = QCheckBox('Сжимать изображения для Telegram')
        self.compress_images.setChecked(True)
        image_layout.addWidget(self.compress_images)

        # Качество сжатия
        quality_layout = QHBoxLayout()
        quality_layout.addWidget(QLabel('Качество сжатия:'))
        self.compression_quality = QSlider(Qt.Orientation.Horizontal)
        self.compression_quality.setMinimum(30)
        self.compression_quality.setMaximum(95)
        self.compression_quality.setValue(85)
        self.quality_label = QLabel('85%')
        self.compression_quality.valueChanged.connect(
            lambda v: self.quality_label.setText(f'{v}%')
        )
        quality_layout.addWidget(self.compression_quality)
        quality_layout.addWidget(self.quality_label)
        image_layout.addLayout(quality_layout)

        layout.addWidget(image_group)
        
        # Кнопка сохранения
        self.save_btn = QPushButton('Сохранить настройки')
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setStyleSheet('''
            QPushButton {
                background: #28a745;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 4px;
                font-size: 16px;
            }
            QPushButton:hover { background: #218838; }
        ''')
        layout.addWidget(self.save_btn)

        # Группа: Предварительный просмотр
        preview_group = QGroupBox("Предварительный просмотр")
        preview_layout = QVBoxLayout(preview_group)

        # Тестовый текст
        preview_layout.addWidget(QLabel('Тестовый текст для предварительного просмотра:'))
        self.preview_text = QTextEdit()
        self.preview_text.setPlaceholderText('Введите текст для предварительного просмотра...')
        self.preview_text.setMaximumHeight(100)
        preview_layout.addWidget(self.preview_text)

        # Кнопка предварительного просмотра
        self.preview_btn = QPushButton('Показать предварительный просмотр')
        self.preview_btn.clicked.connect(self.show_preview)
        preview_layout.addWidget(self.preview_btn)

        # Область предварительного просмотра
        self.preview_area = QTextEdit()
        self.preview_area.setReadOnly(True)
        self.preview_area.setMaximumHeight(150)
        self.preview_area.setStyleSheet('background: #f0f0f0; border: 1px solid #ccc;')
        preview_layout.addWidget(self.preview_area)

        layout.addWidget(preview_group)

        # Кнопки сохранения
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton('Сохранить настройки')
        save_btn.clicked.connect(self.save_settings)
        reset_btn = QPushButton('Сбросить к значениям по умолчанию')
        reset_btn.clicked.connect(self.reset_settings)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(reset_btn)
        layout.addLayout(buttons_layout)

    def load_settings(self):
        """Загрузка сохраненных настроек"""
        # Загрузка настроек ботов
        tg_bots = self.settings.get_telegram_bots()
        
        # Загрузка общих настроек Telegram
        tg_settings = self.settings.get_telegram_settings()
        
        # Установка значений в UI
        self.enable_telegram.setChecked(tg_settings.get('enable_publish', True))
        
        message_format = tg_settings.get('message_format', 'Текст + изображение')
        index = self.message_format.findText(message_format)
        if index >= 0:
            self.message_format.setCurrentIndex(index)
        
        self.max_length.setValue(tg_settings.get('max_length', 400))
        self.message_prefix.setText(tg_settings.get('prefix', '🔎 Quality. Warranty. Confidence.'))
        self.message_suffix.setText(tg_settings.get('suffix', '👉 See more at Global Vendor Network'))
        self.default_url.setText(tg_settings.get('default_url', 'https://gvn.biz/'))
        
        self.compress_images.setChecked(tg_settings.get('compress_images', True))
        self.compression_quality.setValue(tg_settings.get('compression_quality', 85))
        
    def save_settings(self):
        """Сохранение настроек"""
        tg_settings = {
            'enable_publish': self.enable_telegram.isChecked(),
            'message_format': self.message_format.currentText(),
            'max_length': self.max_length.value(),
            'prefix': self.message_prefix.text(),
            'suffix': self.message_suffix.text(),
            'default_url': self.default_url.text(),
            'compress_images': self.compress_images.isChecked(),
            'compression_quality': self.compression_quality.value()
        }
        
        self.settings.set_telegram_settings(tg_settings)
        QMessageBox.information(self, 'Успех', 'Настройки Telegram сохранены!')

    def reset_settings(self):
        """Сбросить к значениям по умолчанию"""
        self.enable_telegram.setChecked(True)
        self.message_format.setCurrentIndex(1)  # Текст + изображение
        self.max_length.setValue(400)
        self.message_prefix.setText('🔎 Quality. Warranty. Confidence.')
        self.message_suffix.setText('👉 See more at Global Vendor Network')
        self.default_url.setText('https://gvn.biz/')
        self.compress_images.setChecked(True)
        self.compression_quality.setValue(85)
        self.quality_label.setText('85%')

    def show_preview(self):
        """Показать предварительный просмотр сообщения"""
        text = self.preview_text.toPlainText()
        if not text:
            text = "Пример текста статьи для демонстрации форматирования сообщения Telegram"
        
        # Форматируем сообщение согласно настройкам
        max_len = self.max_length.value()
        if len(text) > max_len:
            text = text[:max_len-3] + '...'
        
        prefix = self.message_prefix.text() or '🔎 Quality. Warranty. Confidence.'
        suffix = self.message_suffix.text() or '👉 See more at Global Vendor Network'
        url = self.default_url.text() or 'https://gvn.biz/'
        
        formatted_message = f"<b>{prefix}</b>\n\n{text}\n\n<a href=\"{url}\">{suffix}</a>"
        
        self.preview_area.setHtml(formatted_message)

    def get_telegram_settings(self):
        """Получить текущие настройки"""
        return {
            'enabled': self.enable_telegram.isChecked(),
            'format': self.message_format.currentText(),
            'max_length': self.max_length.value(),
            'prefix': self.message_prefix.text(),
            'suffix': self.message_suffix.text(),
            'url': self.default_url.text(),
            'compress_images': self.compress_images.isChecked(),
            'compression_quality': self.compression_quality.value()
        }
