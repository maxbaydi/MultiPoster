from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QProgressBar, QTextEdit, QGroupBox, QCheckBox)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QFont

class MassPublishingDialog(QDialog):
    # Сигналы для управления процессом
    pause_requested = pyqtSignal()
    resume_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Массовая публикация')
        self.setGeometry(200, 200, 600, 500)
        self.setModal(True)
        
        # Получаем настройки
        from config.settings_manager import SettingsManager
        self.settings = SettingsManager()
        
        # Состояние процесса
        self.is_paused = False
        self.is_stopped = False
        self.current_item = 0
        self.total_items = 0
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Заголовок
        title = QLabel('Процесс массовой публикации')
        title.setFont(QFont('Arial', 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Группа: Прогресс
        progress_group = QGroupBox("Прогресс выполнения")
        progress_layout = QVBoxLayout(progress_group)
        
        # Общий прогресс
        self.overall_label = QLabel('Общий прогресс: 0 из 0')
        progress_layout.addWidget(self.overall_label)
        
        self.overall_progress = QProgressBar()
        self.overall_progress.setMinimum(0)
        self.overall_progress.setMaximum(100)
        self.overall_progress.setValue(0)
        progress_layout.addWidget(self.overall_progress)
        
        # Текущий элемент
        self.current_label = QLabel('Текущий элемент: Ожидание...')
        progress_layout.addWidget(self.current_label)
        
        self.current_progress = QProgressBar()
        self.current_progress.setMinimum(0)
        self.current_progress.setMaximum(100)
        self.current_progress.setValue(0)
        progress_layout.addWidget(self.current_progress)
          # Время выполнения
        self.start_time = None
        self.time_label = QLabel('Время выполнения: 00:00:00')
        progress_layout.addWidget(self.time_label)
        
        # Таймер для обновления времени
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        
        # Статус
        self.status_label = QLabel('Статус: Готов к запуску')
        self.status_label.setStyleSheet('color: #00c3ff; font-weight: bold;')
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_group)
        
        # Группа: Настройки публикации
        settings_group = QGroupBox("Настройки публикации")
        settings_layout = QVBoxLayout(settings_group)
        
        # Чекбоксы для выбора платформ
        platforms_layout = QHBoxLayout()
        self.publish_wp = QCheckBox('WordPress')
        self.publish_wp.setChecked(True)  # WordPress всегда включен по умолчанию
        
        # Получаем настройки публикации в Telegram
        tg_settings = self.settings.get_telegram_settings()
        
        self.publish_tg = QCheckBox('Telegram')
        self.publish_tg.setChecked(tg_settings.get('enable_publish', True))
        
        self.publish_fb = QCheckBox('Facebook (будущая функция)')
        self.publish_fb.setEnabled(False)
        
        platforms_layout.addWidget(self.publish_wp)
        platforms_layout.addWidget(self.publish_tg)
        platforms_layout.addWidget(self.publish_fb)
        settings_layout.addLayout(platforms_layout)
        
        layout.addWidget(settings_group)
        
        # Группа: Лог операций
        log_group = QGroupBox("Лог операций")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(150)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet('background: #f8f9fa; font-family: Consolas;')
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        
        self.start_btn = QPushButton('▶ Запустить')
        self.start_btn.setStyleSheet('''
            QPushButton {
                background: #28a745;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover { background: #218838; }
        ''')
        
        self.pause_btn = QPushButton('⏸ Пауза')
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet('''
            QPushButton {
                background: #ffc107;
                color: black;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover { background: #e0a800; }
            QPushButton:disabled { background: #ccc; }
        ''')
        
        self.stop_btn = QPushButton('⏹ Остановить')
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet('''
            QPushButton {
                background: #dc3545;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover { background: #c82333; }
            QPushButton:disabled { background: #ccc; }
        ''')
        
        self.close_btn = QPushButton('Закрыть')
        self.close_btn.setStyleSheet('''
            QPushButton {
                background: #6c757d;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover { background: #5a6268; }
        ''')
        
        buttons_layout.addWidget(self.start_btn)
        buttons_layout.addWidget(self.pause_btn)
        buttons_layout.addWidget(self.stop_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.close_btn)
        
        layout.addLayout(buttons_layout)
          # Подключение сигналов
        self.start_btn.clicked.connect(self.start_process)
        self.pause_btn.clicked.connect(self.pause_process)
        self.stop_btn.clicked.connect(self.stop_process)
        self.close_btn.clicked.connect(self.close_dialog)
        
    def start_process(self):
        """Запустить процесс"""
        from datetime import datetime
        self.start_time = datetime.now()
        self.time_timer.start(1000)  # Обновлять каждую секунду
        
        self.is_paused = False
        self.is_stopped = False
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.status_label.setText('Статус: Выполняется...')
        self.status_label.setStyleSheet('color: #28a745; font-weight: bold;')
        self.add_log('🚀 Процесс массовой публикации запущен')
        
        # Запуск таймера
        self.start_time = None
        self.time_label.setText('Время выполнения: 00:00:00')
        self.time_timer.start(1000)  # Обновление каждую секунду
        
    def pause_process(self):
        """Поставить на паузу или возобновить"""
        if self.is_paused:
            # Возобновить
            self.is_paused = False
            self.pause_btn.setText('⏸ Пауза')
            self.status_label.setText('Статус: Выполняется...')
            self.status_label.setStyleSheet('color: #28a745; font-weight: bold;')
            self.add_log('▶ Процесс возобновлен')
            self.resume_requested.emit()
        else:
            # Пауза
            self.is_paused = True
            self.pause_btn.setText('▶ Продолжить')
            self.status_label.setText('Статус: Приостановлен')
            self.status_label.setStyleSheet('color: #ffc107; font-weight: bold;')
            self.add_log('⏸ Процесс приостановлен')
            self.pause_requested.emit()
            
    def stop_process(self):
        """Остановить процесс"""
        self.is_stopped = True
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setText('⏸ Пауза')
        self.status_label.setText('Статус: Остановлен')
        self.status_label.setStyleSheet('color: #dc3545; font-weight: bold;')
        self.add_log('⏹ Процесс остановлен пользователем')
        self.stop_requested.emit()
        
        # Остановка таймера
        self.time_timer.stop()
        
    def close_dialog(self):
        """Закрыть диалог"""
        if not self.is_stopped and self.pause_btn.isEnabled():
            # Если процесс выполняется, сначала остановить
            self.stop_process()
        self.accept()
        
    def set_total_items(self, count):
        """Установить общее количество элементов"""
        self.total_items = count
        self.overall_progress.setMaximum(count)
        self.overall_label.setText(f'Общий прогресс: 0 из {count}')
        
    def update_overall_progress(self, current):
        """Обновить общий прогресс"""
        self.current_item = current
        self.overall_progress.setValue(current)
        self.overall_label.setText(f'Общий прогресс: {current} из {self.total_items}')
        
    def update_current_item(self, item_name, progress=0):
        """Обновить информацию о текущем элементе"""
        self.current_label.setText(f'Текущий элемент: {item_name}')
        self.current_progress.setValue(progress)
        
    def set_current_progress(self, progress):
        """Установить прогресс текущего элемента"""
        self.current_progress.setValue(progress)
        
    def add_log(self, message):
        """Добавить сообщение в лог"""
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.append(f'[{timestamp}] {message}')

    def finish_process(self, success_count, error_count):
        """Завершить процесс"""
        self.time_timer.stop()
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setText('⏸ Пауза')
        
        if error_count == 0:
            self.status_label.setText('Статус: Завершено успешно')
            self.status_label.setStyleSheet('color: #28a745; font-weight: bold;')
            self.add_log(f'✅ Процесс завершен успешно! Опубликовано: {success_count}')
        else:
            self.status_label.setText('Статус: Завершено с ошибками')
            self.status_label.setStyleSheet('color: #dc3545; font-weight: bold;')
            self.add_log(f'⚠ Процесс завершен. Успешно: {success_count}, Ошибок: {error_count}')
            
        # Остановка таймера
        self.time_timer.stop()
        
    def get_publishing_settings(self):
        """Получить настройки публикации"""
        return {
            'wordpress': self.publish_wp.isChecked(),
            'telegram': self.publish_tg.isChecked(),
            'facebook': self.publish_fb.isChecked()
        }
    
    def update_time(self):
        """Обновить время выполнения"""
        if self.start_time:
            from datetime import datetime
            elapsed = datetime.now() - self.start_time
            hours = elapsed.seconds // 3600
            minutes = (elapsed.seconds % 3600) // 60
            seconds = elapsed.seconds % 60
            self.time_label.setText(f'Время выполнения: {hours:02d}:{minutes:02d}:{seconds:02d}')
