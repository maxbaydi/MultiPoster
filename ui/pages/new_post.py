from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QFileDialog, QMessageBox, QSpinBox, QHBoxLayout, QComboBox, QCheckBox, QGroupBox
from PyQt6.QtCore import QThread, pyqtSignal, QTimer
from api.vsegpt_client import VseGPTClient
from api.wordpress_client import WordPressClient
from api.telegram_client import TelegramClient
from config.env_manager import EnvManager
from config.settings_manager import SettingsManager
from ui.dialogs.mass_publishing_dialog import MassPublishingDialog
import os
import re
import json
import time

class NewPostPage(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = SettingsManager()
        vsegpt = self.settings.get_vsegpt()
        self.gpt = VseGPTClient(vsegpt.get('api_key'), vsegpt.get('url'))
        self.wp_sites = self.settings.get_wordpress_sites()
        self.tg_bots = self.settings.get_telegram_bots()
        self.wp_clients = [WordPressClient(site['url'], site['username'], site['app_password']) for site in self.wp_sites]
        self.wp_categories = [site.get('category_id') for site in self.wp_sites]
        self.tg_clients = [TelegramClient(bot['token'], bot['channel_id']) for bot in self.tg_bots]
        self.image_paths = []
        self.mass_images_root = None
        self.categories = []
        self.category_box = QComboBox()
        self.category_box.addItem('Загрузка...')
        
        # Получаем настройки Telegram
        self.tg_settings = self.settings.get_telegram_settings()
        
        self.watermark_checkbox = QCheckBox('Добавлять вотермарк на изображения')
        self.watermark_checkbox.setChecked(False)
        self.watermark_path = os.path.join('images', 'watermarks', 'watermark.png')
        self.select_watermark_btn = QPushButton('Выбрать изображение для вотермарки')
        self.select_watermark_btn.clicked.connect(self.select_watermark_image)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(14)
        title = QLabel('<h2 style="color:#00c3ff;">New Post</h2>')
        title.setStyleSheet('font-size:28px; font-weight:600; margin-bottom:20px;')
        layout.addWidget(title)
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText('Enter topic...')
        self.topic_input.setStyleSheet('font-size:16px;')
        layout.addWidget(self.topic_input)
        # lcat = QLabel('Рубрика (категория) для WordPress:')
        # lcat.setStyleSheet('font-size:16px; color:#23272e;')
        # layout.addWidget(lcat)
        # self.category_box.setStyleSheet('font-size:16px;')
        # layout.addWidget(self.category_box)
        self.generate_btn = QPushButton('Generate Article')
        self.generate_btn.setStyleSheet('margin-bottom: 8px;')
        self.generate_btn.clicked.connect(self.generate_article)
        layout.addWidget(self.generate_btn)
        self.body_edit = QTextEdit()
        self.body_edit.setStyleSheet('font-size:16px; background:#fff; border-radius:8px;')
        layout.addWidget(self.body_edit)
        self.attach_btn = QPushButton('Attach Images')
        self.attach_btn.clicked.connect(self.attach_images)
        layout.addWidget(self.attach_btn)
        
        # Группа настроек публикации
        publish_group = QGroupBox("Настройки публикации")
        publish_layout = QVBoxLayout(publish_group)
        
        platforms_layout = QHBoxLayout()
        self.publish_wp = QCheckBox('WordPress')
        self.publish_wp.setChecked(True)
        
        self.publish_tg = QCheckBox('Telegram')
        # Устанавливаем значение из глобальных настройка
        self.publish_tg.setChecked(self.tg_settings.get('enable_publish', True) and bool(self.tg_clients))
        
        self.publish_fb = QCheckBox('Facebook (будущая функция)')
        self.publish_fb.setEnabled(False)
        
        # Добавляем надпись о том, что глобальные настройки находятся на странице Telegram Settings
        tg_note = QLabel('<i>Примечание: глобальные настройки Telegram публикации находятся в разделе "Telegram Settings"</i>')
        tg_note.setStyleSheet('color: gray; font-size: 12px;')
        
        platforms_layout.addWidget(self.publish_wp)
        platforms_layout.addWidget(self.publish_tg)
        platforms_layout.addWidget(self.publish_fb)
        publish_layout.addLayout(platforms_layout)
        publish_layout.addWidget(tg_note)
        
        layout.addWidget(publish_group)
        
        self.publish_btn = QPushButton('Publish')
        self.publish_btn.clicked.connect(self.publish_post)
        layout.addWidget(self.publish_btn)
        self.mass_img_btn = QPushButton('Select Root Images Folder (with subfolders)')
        self.mass_img_btn.clicked.connect(self.select_images_root)
        layout.addWidget(self.mass_img_btn)
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel('Delay (sec):'))
        self.delay_spin = QSpinBox()
        self.delay_spin.setMinimum(0)
        self.delay_spin.setMaximum(3600)
        self.delay_spin.setValue(10)
        hbox.addWidget(self.delay_spin)
        layout.addLayout(hbox)
        self.mass_btn = QPushButton('Mass Generate & Publish (JSON)')
        self.mass_btn.clicked.connect(self.mass_generate)
        layout.addWidget(self.mass_btn)
        layout.addWidget(self.watermark_checkbox)
        layout.addWidget(self.select_watermark_btn)
        # self.load_categories()

    def load_categories(self):
        pass  # больше не требуется

    def replace_or_distribute_images(self, html, image_urls):
        # Найти все <img ...>
        img_tags = list(re.finditer(r"<img[^>]*src=['\"][^'\"]+['\"][^>]*>", html))
        result = html
        used = 0
        # Заменить существующие <img ...> на реальные ссылки
        for i, match in enumerate(img_tags):
            if used < len(image_urls):
                new_tag = f"<img src='{image_urls[used]}' style='width:100%;height:auto;margin:20px 0;'/>"
                result = result.replace(match.group(0), new_tag, 1)
                used += 1
            else:
                # Если ссылок не хватает — удалить лишние <img>
                result = result.replace(match.group(0), '', 1)
        # Если ссылок больше, чем <img> — равномерно вставить оставшиеся
        if used < len(image_urls):
            paragraphs = re.split(r'(</p>|</ul>|</ol>)', result)
            step = max(1, len(paragraphs) // (len(image_urls) - used + 1))
            insert_idx = step
            for url in image_urls[used:]:
                if insert_idx < len(paragraphs):
                    paragraphs[insert_idx] += f"<img src='{url}' style='width:100%;height:auto;margin:20px 0;'/>"
                    insert_idx += step
                else:
                    paragraphs[-1] += f"<img src='{url}' style='width:100%;height:auto;margin:20px 0;'/>"
            result = ''.join(paragraphs)
        return result

    def build_gpt_prompt(self, topic, image_urls=None, subtopics=None):
        images = ''
        if image_urls:
            images = '\n'.join(image_urls)
        subtopics_str = ''
        if subtopics:
            subtopics_str = '\nSubtopics to cover as sections in the article:\n' + '\n'.join(f'- {s}' for s in subtopics)
        return f'''
You are an expert SEO copywriter.
Generate a full, SEO-optimized article in English for the topic: "{topic}".
Requirements:
- Title (h1)
- Main body (HTML formatted, with subheadings, lists, etc.)
- 3-5 relevant tags (comma separated)
- Insert provided image URLs as <img> tags in appropriate places in the article (use all images)
- The article must be at least 1500 words
- Write a short, catchy, selling summary (max 300 characters) for Telegram, with a call to action and only one link at the end, wrapped in the text <a href='https://gvn.biz/'>Global Vendor Network</a>. Do not include any other links or URLs in the summary.
{subtopics_str}
- Output strictly in the following JSON format:
{{
  "title": "...",
  "body": "...",
  "tags": "...",
  "telegram_summary": "..."
}}
Provided image URLs (use all):
{images}
'''

    def format_telegram_post(self, text, url):
        text = text.strip()
        
        # Используем настройки из глобальных настроек Telegram
        max_length = self.tg_settings.get('max_length', 400)
        prefix = self.tg_settings.get('prefix', '🔎 Quality. Warranty. Confidence.')
        suffix = self.tg_settings.get('suffix', '👉 See more at Global Vendor Network')
        default_url = self.tg_settings.get('default_url', 'https://gvn.biz/')
        
        # Если URL не указан, используем URL по умолчанию
        if not url:
            url = default_url
            
        # Ограничиваем длину текста
        if len(text) > max_length:
            text = text[:max_length-3] + '...'
        
        # Форматируем сообщение с префиксом и суффиксом
        return f"<b>{prefix}</b>\n\n{text}\n\n{suffix.replace('{url}', url)}"

    def generate_article(self):
        topic = self.topic_input.text().strip()
        if not topic:
            QMessageBox.warning(self, 'Error', 'Enter a topic!')
            return
        # Используем новый промт
        prompt = self.build_gpt_prompt(topic, image_urls=None)
        resp = self.gpt.generate_article(topic)
        match = re.search(r'\{[\s\S]+\}', resp['choices'][0]['message']['content'])
        if not match:
            QMessageBox.warning(self, 'Error', 'No JSON in GPT response!')
            return
        article = json.loads(match.group(0))
        self.generated = article
        if self.image_paths:
            media_urls = []
            for img in self.image_paths:
                _, url = self.wp_clients[0].upload_media(img)
                media_urls.append(url)
            article['body'] = self.replace_or_distribute_images(article['body'], media_urls)
        self.body_edit.setPlainText(article['body'])

    def attach_images(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Select Images', '', 'Images (*.png *.jpg *.jpeg)')
        if files:
            self.image_paths = files
            QMessageBox.information(self, 'Images', f'Attached: {len(files)} images')

    def publish_post(self):
        if not hasattr(self, 'generated'):
            QMessageBox.warning(self, 'Error', 'Generate article first!')
            return
        
        # Проверяем, что выбрана хотя бы одна платформа
        if not (self.publish_wp.isChecked() or self.publish_tg.isChecked()):
            QMessageBox.warning(self, 'Error', 'Выберите хотя бы одну платформу для публикации!')
            return
        
        # Проверяем доступность платформ
        if self.publish_wp.isChecked() and not self.wp_clients:
            QMessageBox.warning(self, 'Error', 'WordPress не настроен!')
            return
            
        # Проверяем доступность Telegram только если он выбран для публикации
        if self.publish_tg.isChecked():
            # Проверяем глобальные настройки Telegram
            if not self.tg_settings.get('enable_publish', True):
                QMessageBox.warning(self, 'Error', 'Публикация в Telegram отключена в глобальных настройках!')
                return
                
            # Проверяем, настроены ли боты
            if not self.tg_clients:
                QMessageBox.warning(self, 'Error', 'Telegram не настроен!')
                return
            
        media_ids = []
        post_links = []
        
        # Загрузка изображений только если публикуем в WordPress
        if self.publish_wp.isChecked():
            for img in self.image_paths:
                # Если чекбокс включён, применяем вотермарк
                if self.watermark_checkbox.isChecked():
                    from api.watermark import add_image_watermark
                    import os
                    wm_path = self.watermark_path
                    output_img = img.replace('.', '_wm.')
                    from PIL import Image
                    with Image.open(img) as im:
                        w, h = im.size
                    # Задаем масштаб вотермарки (например, 20% от ширины исходного изображения)
                    watermark_scale = 0.2
                    # Временно открываем вотермарк, чтобы получить его исходные пропорции
                    try:
                        with Image.open(wm_path) as wm_img:
                            wm_w_orig, wm_h_orig = wm_img.size
                        # Рассчитываем новый размер на основе масштаба
                        wm_w_scaled = int(w * watermark_scale)
                        wm_h_scaled = int(wm_h_orig * (wm_w_scaled / wm_w_orig))
                        # Рассчитываем позицию для центрирования scaled вотермарки
                        pos = ((w - wm_w_scaled) // 2, (h - wm_h_scaled) // 2)
                        add_image_watermark(img, output_img, wm_path, position=pos, opacity=100, watermark_scale=watermark_scale)
                        upload_path = output_img
                    except FileNotFoundError:
                        QMessageBox.warning(self, 'Error', f'Файл вотермарки не найден: {wm_path}')
                        upload_path = img # Загружаем оригинальное изображение, если вотермарк не найден
                    except Exception as e:
                         QMessageBox.warning(self, 'Error', f'Ошибка при обработке вотермарки: {e}')
                         upload_path = img # Загружаем оригинальное изображение в случае ошибки обработки
                else:
                    upload_path = img
                media_id, _ = self.wp_clients[0].upload_media(upload_path)  # Для первой WP
                media_ids.append(media_id)
            
            # Публикация на все WP сайты с их категориями
            for i, wp in enumerate(self.wp_clients):
                try:
                    post = wp.create_post(
                        title=self.generated['title'],
                        content=self.generated['body'],
                        status='publish',
                        media_ids=media_ids if media_ids else None,
                        category_id=self.wp_categories[i] if i < len(self.wp_categories) and self.wp_categories[i] else None
                    )
                    post_links.append(post['link'])
                except Exception as e:
                    post_links.append(f'Ошибка: {e}')
        
        # Публикация в Telegram только если выбрано
        if self.publish_tg.isChecked() and self.tg_clients:
            tg_text = self.format_telegram_post(self.generated['telegram_summary'], post_links[0] if post_links else '')
            for tg in self.tg_clients:
                try:
                    if self.image_paths and len(self.image_paths) > 0:
                        tg.send_photo(self.image_paths[0], caption=tg_text, parse_mode='HTML')
                    else:
                        tg.send_message(tg_text, parse_mode='HTML')
                except Exception as e:
                    pass
        
        # Формируем сообщение об успехе
        published_to = []
        if self.publish_wp.isChecked():
            published_to.append('WordPress')
        if self.publish_tg.isChecked():
            published_to.append('Telegram')
            
        QMessageBox.information(self, 'Success', f'Post published to: {", ".join(published_to)}!')

    def select_images_root(self):
        dir = QFileDialog.getExistingDirectory(self, 'Select Root Images Folder')
        if dir:
            self.mass_images_root = dir
            QMessageBox.information(self, 'Images Root', f'Selected: {dir}')

    def normalize_name(self, name):
        name = name.lower()
        name = re.sub(r'[^a-z0-9]+', '_', name)  # всё, что не буква/цифра — в _
        name = re.sub(r'_+', '_', name)         # несколько _ подряд — в один
        name = name.strip('_')
        return name

    def mass_generate(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Select JSON', '', 'JSON Files (*.json)')
        if not file:
            return
        
        try:
            with open(file, 'r', encoding='utf-8') as f:
                items = json.load(f)
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'Ошибка чтения файла: {str(e)}')
            return
            
        if not isinstance(items, list):
            QMessageBox.warning(self, 'Error', 'JSON file must contain a list of objects!')
            return
            
        if not items:
            QMessageBox.information(self, 'Info', 'JSON файл пустой!')
            return
        
        # Создаем и показываем диалог прогресса
        dialog = MassPublishingDialog(self)
        dialog.set_total_items(len(items))
        
        # Настраиваем воркер
        self.mass_worker = MassPublishingWorker(items, {
            'wp_clients': self.wp_clients,
            'wp_categories': self.wp_categories,
            'tg_clients': self.tg_clients,
            'gpt': self.gpt,
            'mass_images_root': self.mass_images_root,
            'watermark_settings': {
                'enabled': self.watermark_checkbox.isChecked(),
                'path': self.watermark_path
            }
        }, self)
        
        # Устанавливаем задержку
        self.mass_worker.set_delay(self.delay_spin.value())
        
        # Подключаем сигналы
        self.mass_worker.progress_updated.connect(dialog.update_overall_progress)
        self.mass_worker.item_progress_updated.connect(dialog.update_current_item)
        self.mass_worker.log_message.connect(dialog.add_log)
        self.mass_worker.finished.connect(dialog.finish_process)
        
        # Подключаем сигналы управления
        dialog.pause_requested.connect(self.mass_worker.pause)
        dialog.resume_requested.connect(self.mass_worker.resume)
        dialog.stop_requested.connect(self.mass_worker.stop)
        
        # Автозапуск процесса при открытии диалога
        def start_when_shown():
            publishing_settings = dialog.get_publishing_settings()
            
            # Проверяем настройки
            error_messages = []
            if publishing_settings['wordpress'] and not self.wp_clients:
                error_messages.append('WordPress не настроен')
            # Проверяем настройки Telegram только если пользователь выбрал публикацию в Telegram
            if publishing_settings['telegram']:
                if not self.tg_clients:
                    error_messages.append('Telegram не настроен')
            if not self.mass_images_root:
                error_messages.append('Не выбрана папка с изображениями')
            if not (publishing_settings['wordpress'] or publishing_settings['telegram']):
                error_messages.append('Не выбрана ни одна платформа для публикации')
                
            if error_messages:
                QMessageBox.warning(self, 'Ошибка конфигурации', '\n'.join(error_messages))
                dialog.close()
                return
                
            # Обновляем настройки воркера
            self.mass_worker.settings.update({
                'publishing_platforms': publishing_settings
            })
            
            # Запускаем процесс
            self.mass_worker.start()
            dialog.start_process()
        
        # Подключаем автозапуск к сигналу показа диалога
        timer = QTimer()
        timer.singleShot(100, start_when_shown)
        
        # Показываем диалог
        dialog.exec()

    def select_watermark_image(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Выберите изображение вотермарки', '', 'Images (*.png *.jpg *.jpeg)')
        if file:
            self.watermark_path = file
            QMessageBox.information(self, 'Вотермарк', f'Выбрано: {file}')

class MassPublishingWorker(QThread):
    """Воркер для массовой публикации в отдельном потоке"""
    progress_updated = pyqtSignal(int)  # Общий прогресс
    item_progress_updated = pyqtSignal(str, int)  # Прогресс текущего элемента (название, прогресс)
    log_message = pyqtSignal(str)  # Сообщение для лога
    finished = pyqtSignal(int, int)  # Завершено (успешных, ошибок)
    
    def __init__(self, items, settings, parent=None):
        super().__init__(parent)
        self.items = items
        self.settings = settings
        self.parent_widget = parent
        self.is_paused = False
        self.is_stopped = False
        self.delay = 10
        
    def run(self):
        """Основной метод выполнения массовой публикации"""
        success_count = 0
        error_count = 0
        
        for i, item in enumerate(self.items):
            if self.is_stopped:
                break
                
            # Ожидание, если процесс на паузе
            while self.is_paused and not self.is_stopped:
                self.msleep(100)
                
            if self.is_stopped:
                break
                
            try:
                # Обновляем прогресс
                topic = item.get('topic', 'Неизвестная тема')
                self.item_progress_updated.emit(topic, 0)
                self.log_message.emit(f'Начинаю обработку: {topic}')
                
                # Обработка элемента
                result = self.process_single_item(item, i)
                
                if result:
                    success_count += 1
                    self.log_message.emit(f'✅ Успешно опубликовано: {topic}')
                else:
                    error_count += 1
                    self.log_message.emit(f'❌ Ошибка при публикации: {topic}')
                    
                # Обновляем общий прогресс
                self.progress_updated.emit(i + 1)
                
                # Задержка между публикациями
                if i < len(self.items) - 1:  # Не ждать после последнего элемента
                    self.log_message.emit(f'Ожидание {self.delay} секунд...')
                    for _ in range(self.delay * 10):  # Разбиваем на 100мс интервалы
                        if self.is_stopped:
                            break
                        while self.is_paused and not self.is_stopped:
                            self.msleep(100)
                        self.msleep(100)
                        
            except Exception as e:
                error_count += 1
                self.log_message.emit(f'❌ Критическая ошибка при обработке {topic}: {str(e)}')
                
        self.finished.emit(success_count, error_count)
        
    def process_single_item(self, item, index):
        """Обработка одного элемента"""
        try:
            brand = item.get('brand', '')
            topic = item.get('topic', '')
            subtopics = item.get('subtopics', [])
            
            if not topic:
                self.log_message.emit('Пропускаю элемент без темы')
                return False
                
            full_topic = f"{brand}: {topic}" if brand else topic
            
            # Этап 1: Поиск папки с изображениями (25%)
            self.item_progress_updated.emit(topic, 25)
            topic_norm = self.parent_widget.normalize_name(topic)
            brand_topic_norm = self.parent_widget.normalize_name(f"{brand}_{topic}") if brand else topic_norm
            
            subfolder = None
            if self.settings.get('mass_images_root'):
                for folder in os.listdir(self.settings['mass_images_root']):
                    folder_path = os.path.join(self.settings['mass_images_root'], folder)
                    if os.path.isdir(folder_path):
                        if self.parent_widget.normalize_name(folder) in [topic_norm, brand_topic_norm]:
                            subfolder = folder_path
                            break
            
            # Этап 2: Загрузка изображений (50%)
            self.item_progress_updated.emit(topic, 50)
            image_urls, image_paths, media_ids = [], [], []
            
            if subfolder and self.settings['publishing_platforms'].get('wordpress'):
                try:
                    for fname in sorted(os.listdir(subfolder)):
                        if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                            img_path = os.path.join(subfolder, fname)
                            
                            # Проверяем, нужно ли добавлять вотермарк
                            if self.settings.get('watermark_settings', {}).get('enabled'):
                                from api.watermark import add_image_watermark
                                wm_path = self.settings['watermark_settings'].get('path')
                                output_img = img_path.replace('.', '_wm.')
                                
                                # Получаем размеры исходного изображения
                                from PIL import Image
                                try:
                                    with Image.open(img_path) as im:
                                        w, h = im.size
                                    
                                    # Масштаб вотермарки
                                    watermark_scale = 0.2
                                    
                                    # Открываем вотермарк и получаем его пропорции
                                    with Image.open(wm_path) as wm_img:
                                        wm_w_orig, wm_h_orig = wm_img.size
                                    
                                    # Рассчитываем новый размер на основе масштаба
                                    wm_w_scaled = int(w * watermark_scale)
                                    wm_h_scaled = int(wm_h_orig * (wm_w_scaled / wm_w_orig))
                                    
                                    # Рассчитываем позицию для центрирования водяного знака
                                    pos = ((w - wm_w_scaled) // 2, (h - wm_h_scaled) // 2)
                                    
                                    # Применяем вотермарк
                                    add_image_watermark(img_path, output_img, wm_path, position=pos, opacity=100, watermark_scale=watermark_scale)
                                    
                                    # Используем изображение с водяным знаком
                                    upload_path = output_img
                                    self.log_message.emit(f'Добавлен вотермарк на изображение: {os.path.basename(img_path)}')
                                    
                                except FileNotFoundError:
                                    self.log_message.emit(f'Файл вотермарки не найден: {wm_path}')
                                    upload_path = img_path  # Используем оригинальное изображение
                                except Exception as e:
                                    self.log_message.emit(f'Ошибка при обработке вотермарки: {str(e)}')
                                    upload_path = img_path  # Используем оригинальное изображение
                            else:
                                # Используем изображение без вотермарка
                                upload_path = img_path
                                
                            # Загружаем изображение
                            media_id, media_url = self.settings['wp_clients'][0].upload_media(upload_path)
                            image_paths.append(img_path)  # Сохраняем оригинальный путь для Telegram
                            image_urls.append(media_url)
                            media_ids.append(media_id)
                except Exception as e:
                    self.log_message.emit(f'Ошибка загрузки изображений: {str(e)}')
            
            # Этап 3: Генерация статьи (75%)
            self.item_progress_updated.emit(topic, 75)
            prompt = self.parent_widget.build_gpt_prompt(full_topic, image_urls=image_urls, subtopics=subtopics)
            resp = self.settings['gpt'].generate_article(prompt)
            
            match = re.search(r'\{[\s\S]+\}', resp['choices'][0]['message']['content'])
            if not match:
                self.log_message.emit('Не удалось получить JSON от GPT')
                return False
                
            article = json.loads(match.group(0))
            if image_urls:
                article['body'] = self.parent_widget.replace_or_distribute_images(article['body'], image_urls)
            
            # Этап 4: Публикация (100%)
            self.item_progress_updated.emit(topic, 100)
            
            post_link = None
            
            # Публикация в WordPress
            if self.settings['publishing_platforms'].get('wordpress') and self.settings['wp_clients']:
                try:
                    post = self.settings['wp_clients'][0].create_post(
                        title=article['title'],
                        content=article['body'],
                        status='publish',
                        media_ids=media_ids if media_ids else None,
                        category_id=self.settings['wp_categories'][0] if self.settings.get('wp_categories') and self.settings['wp_categories'] else None
                    )
                    post_link = post['link']
                    self.log_message.emit(f'WordPress: ✅ Опубликовано')
                except Exception as e:
                    self.log_message.emit(f'WordPress: ❌ Ошибка - {str(e)}')
            
            # Публикация в Telegram
            if self.settings['publishing_platforms'].get('telegram') and self.settings['tg_clients']:
                try:
                    tg_text = self.parent_widget.format_telegram_post(article['telegram_summary'], post_link or '')
                    if image_paths:
                        self.settings['tg_clients'][0].send_photo(image_paths[0], caption=tg_text, parse_mode='HTML')
                    else:
                        self.settings['tg_clients'][0].send_message(tg_text, parse_mode='HTML')
                    self.log_message.emit(f'Telegram: ✅ Опубликовано')
                except Exception as e:
                    self.log_message.emit(f'Telegram: ❌ Ошибка - {str(e)}')
            
            return True
            
        except Exception as e:
            self.log_message.emit(f'Критическая ошибка: {str(e)}')
            return False
            
    def pause(self):
        """Поставить на паузу"""
        self.is_paused = True
        
    def resume(self):
        """Возобновить"""
        self.is_paused = False
        
    def stop(self):
        """Остановить"""
        self.is_stopped = True
        
    def set_delay(self, delay):
        """Установить задержку между публикациями"""
        self.delay = delay