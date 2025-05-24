from config.env_manager import EnvManager
from api.wordpress_client import WordPressClient
import os

if __name__ == '__main__':
    env = EnvManager()
    wp = WordPressClient(env.get('WP_URL'), env.get('WP_USERNAME'), env.get('WP_APP_PASSWORD'))
    print('--- Тест загрузки изображения ---')
    # Используем стандартную картинку Python, если нет своей
    test_image = 'test_image.jpg'
    if not os.path.exists(test_image):
        # Скачиваем тестовую картинку
        import requests
        url = 'https://www.python.org/static/community_logos/python-logo.png'
        r = requests.get(url)
        with open(test_image, 'wb') as f:
            f.write(r.content)
    try:
        media_id, media_url = wp.upload_media(test_image)
        print('Изображение успешно загружено!')
        print('Media ID:', media_id)
        print('URL:', media_url)
    except Exception as e:
        print('Ошибка загрузки:', e) 