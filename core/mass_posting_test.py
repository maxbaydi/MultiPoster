import json
from config.env_manager import EnvManager
from api.wordpress_client import WordPressClient
from api.vsegpt_client import VseGPTClient
from api.telegram_client import TelegramClient
import os
import time

def load_topics():
    # Пример списка тем
    return [
        "How to choose a supplier in China",
        "Top 5 mistakes when importing goods",
        "Inspection and warranty for products"
    ]

def download_image(url, filename):
    import requests
    r = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(r.content)
    return filename

if __name__ == '__main__':
    env = EnvManager()
    wp = WordPressClient(env.get('WP_URL'), env.get('WP_USERNAME'), env.get('WP_APP_PASSWORD'))
    gpt = VseGPTClient(env.get('VSEGPT_API_KEY'), env.get('VSEGPT_URL'))
    tg = TelegramClient(env.get('TELEGRAM_BOT_TOKEN'), env.get('TELEGRAM_CHANNEL_ID'))

    topics = load_topics()
    for topic in topics:
        print(f'\n=== Генерация статьи для темы: {topic} ===')
        gpt_resp = gpt.generate_article(topic)
        # Парсим JSON из ответа
        import re
        match = re.search(r'\{[\s\S]+\}', gpt_resp['choices'][0]['message']['content'])
        if not match:
            print('Ошибка: не найден JSON в ответе GPT')
            continue
        article = json.loads(match.group(0))
        # Загрузка изображения (пример: одна картинка)
        image_url = 'https://www.python.org/static/community_logos/python-logo.png'
        image_path = download_image(image_url, f'{topic[:10]}.jpg')
        media_id, media_url = wp.upload_media(image_path)
        # Публикация в WordPress
        post = wp.create_post(
            title=article['title'],
            content=article['body'],
            status='publish',
            media_ids=[media_id]
        )
        print('Пост опубликован:', post['link'])
        # Публикация в Telegram
        tg.send_message(article['telegram_summary'] + f"\n<a href='{post['link']}'>Global Vendor Network</a>", parse_mode='HTML')
        tg.send_photo(image_path, caption=article['telegram_summary'], parse_mode='HTML')
        print('Пост отправлен в Telegram')
        time.sleep(2)  # чтобы не спамить API 