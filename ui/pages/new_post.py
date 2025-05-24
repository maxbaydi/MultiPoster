from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QFileDialog, QMessageBox, QSpinBox, QHBoxLayout, QComboBox, QCheckBox
from api.vsegpt_client import VseGPTClient
from api.wordpress_client import WordPressClient
from api.telegram_client import TelegramClient
from config.env_manager import EnvManager
from config.settings_manager import SettingsManager
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
        self.publish_btn = QPushButton('Publish (WP + TG)')
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
        self.delay_spin.setValue(2)
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
    def get_selected_category_id(self):
        return None  # больше не требуется

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
        if len(text) > 400:
            text = text[:397] + '...'
        text = f"<b>🔎 Quality. Warranty. Confidence.</b>\n\n{text}\n\n👉 <a href=\"{url}\">See more at Global Vendor Network</a>"
        return text

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
        media_ids = []
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
        post_links = []
        for i, wp in enumerate(self.wp_clients):
            try:
                post = wp.create_post(
                    title=self.generated['title'],
                    content=self.generated['body'],
                    status='publish',
                    media_ids=media_ids if media_ids else None,
                    category_id=self.wp_categories[i] if self.wp_categories[i] else None
                )
                post_links.append(post['link'])
            except Exception as e:
                post_links.append(f'Ошибка: {e}')
        # Публикация во все TG боты
        tg_text = self.format_telegram_post(self.generated['telegram_summary'], post_links[0] if post_links else '')
        for tg in self.tg_clients:
            try:
                if self.image_paths:
                    tg.send_photo(self.image_paths[0], caption=tg_text, parse_mode='HTML')
                else:
                    tg.send_message(tg_text, parse_mode='HTML')
            except Exception as e:
                pass
        QMessageBox.information(self, 'Success', 'Post published to all sites and bots!')

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
        with open(file, 'r', encoding='utf-8') as f:
            items = json.load(f)
        if not isinstance(items, list):
            QMessageBox.warning(self, 'Error', 'JSON file must contain a list of objects!')
            return
        delay = self.delay_spin.value()
        category_id = self.get_selected_category_id()
        if not category_id:
            QMessageBox.warning(self, 'Error', 'Выберите рубрику для публикации!')
            return
        i = 0
        while i < len(items):
            item = items[i]
            brand = item.get('brand', '')
            topic = item.get('topic', '')
            subtopics = item.get('subtopics', [])
            if not topic:
                i += 1
                continue
            full_topic = f"{brand}: {topic}" if brand else topic
            topic_norm = self.normalize_name(topic)
            brand_topic_norm = self.normalize_name(f"{brand}_{topic}") if brand else topic_norm
            subfolder = None
            for folder in os.listdir(self.mass_images_root):
                folder_path = os.path.join(self.mass_images_root, folder)
                if os.path.isdir(folder_path):
                    if self.normalize_name(folder) in [topic_norm, brand_topic_norm]:
                        subfolder = folder_path
                        break
            if not subfolder:
                QMessageBox.warning(self, 'Error', f'No image folder found for topic: {topic}. Skipping.')
                i += 1
                continue
            try:
                image_urls, image_paths, media_ids = [], [], []
                for fname in sorted(os.listdir(subfolder)):
                    if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                        img_path = os.path.join(subfolder, fname)
                        media_id, media_url = self.wp_clients[0].upload_media(img_path)
                        image_paths.append(img_path)
                        image_urls.append(media_url)
                        media_ids.append(media_id)
                prompt = self.build_gpt_prompt(full_topic, image_urls=image_urls, subtopics=subtopics)
                resp = self.gpt.generate_article(prompt)
                match = re.search(r'\{[\s\S]+\}', resp['choices'][0]['message']['content'])
                if not match:
                    QMessageBox.warning(self, 'Error', f'No JSON in GPT response for topic: {topic}. Skipping.')
                    i += 1
                    continue
                article = json.loads(match.group(0))
                if image_urls:
                    article['body'] = self.replace_or_distribute_images(article['body'], image_urls)
                post = self.wp_clients[0].create_post(
                    title=article['title'],
                    content=article['body'],
                    status='publish',
                    media_ids=media_ids if media_ids else None,
                    category_id=category_id
                )
                tg_text = self.format_telegram_post(article['telegram_summary'], post['link'])
                if image_paths:
                    self.tg_clients[0].send_photo(image_paths[0], caption=tg_text, parse_mode='HTML')
                else:
                    self.tg_clients[0].send_message(tg_text, parse_mode='HTML')
                items.pop(i)
                with open(file, 'w', encoding='utf-8') as f:
                    json.dump(items, f, ensure_ascii=False, indent=2)
                time.sleep(delay)
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Error publishing topic: {topic}\n{str(e)}')
                i += 1
        if not items:
            QMessageBox.information(self, 'Done', 'All topics processed. JSON file is now empty!')
        else:
            QMessageBox.information(self, 'Done', f'Not all topics published. Remaining: {len(items)}')

    def select_watermark_image(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Выберите изображение вотермарки', '', 'Images (*.png *.jpg *.jpeg)')
        if file:
            self.watermark_path = file
            QMessageBox.information(self, 'Вотермарк', f'Выбрано: {file}')