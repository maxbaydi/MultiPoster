import json
import time
import os
from config.env_manager import EnvManager
from api.wordpress_client import WordPressClient
from api.vsegpt_client import VseGPTClient
from api.telegram_client import TelegramClient

def normalize_name(name):
    import re
    name = name.lower()
    name = re.sub(r'[^a-z0-9]+', '_', name)
    name = re.sub(r'_+', '_', name)
    name = name.strip('_')
    return name

def build_gpt_prompt(topic, image_urls=None, subtopics=None):
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

def format_telegram_post(text, url):
    text = text.strip()
    if len(text) > 400:
        text = text[:397] + '...'
    text = f"<b>🔎 Quality. Warranty. Confidence.</b>\n\n{text}\n\n👉 <a href=\"{url}\">See more at Global Vendor Network</a>"
    return text

if __name__ == '__main__':
    # Один объект из theme.json
    item = {
      "brand": "Schneider Electric",
      "topic": "Schneider Electric: Комплексные решения для автоматизации и энергоэффективности",
      "subtopics": [
        "Контроллеры M258 и TM258: высокая производительность в промышленных системах",
        "Человеко-машинные интерфейсы (HMI) HMIGTO: визуализация процессов",
        "Модули ввода/вывода TM5 и TM3: расширение возможностей автоматизации",
        "Энергосберегающие двигатели и частотные преобразователи Altivar"
      ]
    }
    env = EnvManager()
    wp = WordPressClient(env.get('WP_URL'), env.get('WP_USERNAME'), env.get('WP_APP_PASSWORD'))
    gpt = VseGPTClient(env.get('VSEGPT_API_KEY'), env.get('VSEGPT_URL'))
    tg = TelegramClient(env.get('TELEGRAM_BOT_TOKEN'), env.get('TELEGRAM_CHANNEL_ID'))
    brand = item.get('brand', '')
    topic = item.get('topic', '')
    subtopics = item.get('subtopics', [])
    full_topic = f"{brand}: {topic}" if brand else topic
    # Поиск папки с изображениями
    mass_images_root = './images'  # путь к папке с папками
    topic_norm = normalize_name(topic)
    brand_topic_norm = normalize_name(f"{brand}_{topic}") if brand else topic_norm
    subfolder = None
    for folder in os.listdir(mass_images_root):
        folder_path = os.path.join(mass_images_root, folder)
        if os.path.isdir(folder_path):
            if normalize_name(folder) in [topic_norm, brand_topic_norm]:
                subfolder = folder_path
                break
    image_urls, image_paths, media_ids = [], [], []
    if subfolder:
        for fname in sorted(os.listdir(subfolder)):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(subfolder, fname)
                media_id, media_url = wp.upload_media(img_path)
                image_paths.append(img_path)
                image_urls.append(media_url)
                media_ids.append(media_id)
    prompt = build_gpt_prompt(full_topic, image_urls=image_urls, subtopics=subtopics)
    resp = gpt.generate_article(prompt)
    import re
    match = re.search(r'\{[\s\S]+\}', resp['choices'][0]['message']['content'])
    if not match:
        print('No JSON in GPT response!')
        exit(1)
    article = json.loads(match.group(0))
    # Замена заглушек на реальные ссылки
    def replace_or_distribute_images(html, image_urls):
        img_tags = list(re.finditer(r"<img[^>]*src=['\"][^'\"]+['\"][^>]*>", html))
        result = html
        used = 0
        for i, match in enumerate(img_tags):
            if used < len(image_urls):
                new_tag = f"<img src='{image_urls[used]}' style='width:100%;height:auto;margin:20px 0;'/>"
                result = result.replace(match.group(0), new_tag, 1)
                used += 1
            else:
                result = result.replace(match.group(0), '', 1)
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
    if image_urls:
        article['body'] = replace_or_distribute_images(article['body'], image_urls)
    post = wp.create_post(
        title=article['title'],
        content=article['body'],
        status='publish',
        media_ids=media_ids if media_ids else None
    )
    tg_text = format_telegram_post(article['telegram_summary'], post['link'])
    if image_paths:
        tg.send_photo(image_paths[0], caption=tg_text, parse_mode='HTML')
    else:
        tg.send_message(tg_text, parse_mode='HTML')
    print('Пост успешно опубликован!')
    print('WordPress:', post['link']) 