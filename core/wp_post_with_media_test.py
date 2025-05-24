from config.env_manager import EnvManager
from api.wordpress_client import WordPressClient

if __name__ == '__main__':
    env = EnvManager()
    wp = WordPressClient(env.get('WP_URL'), env.get('WP_USERNAME'), env.get('WP_APP_PASSWORD'))
    print('--- Публикация поста с изображением ---')
    # Используем ID и URL из предыдущего теста
    media_id = 8616  # Замените на актуальный ID, если нужно
    try:
        post = wp.create_post(
            title='Пост с картинкой из MultiPoster',
            content='<h2>Пост с картинкой</h2><img src="https://gvn.biz/wp-content/uploads/2025/05/test_image.png" alt="test"/><p>Проверка публикации с media.</p>',
            status='publish',
            media_ids=[media_id]
        )
        print('Пост с изображением успешно опубликован!')
        print('ID:', post['id'])
        print('URL:', post['link'])
    except Exception as e:
        print('Ошибка публикации:', e) 