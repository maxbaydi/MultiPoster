from config.env_manager import EnvManager
from api.wordpress_client import WordPressClient

if __name__ == '__main__':
    env = EnvManager()
    wp = WordPressClient(env.get('WP_URL'), env.get('WP_USERNAME'), env.get('WP_APP_PASSWORD'))
    print('--- Тест публикации поста ---')
    try:
        post = wp.create_post(
            title='Тестовый пост из MultiPoster',
            content='<h2>Это тестовый пост</h2><p>Проверка публикации через Python.</p>',
            status='publish'
        )
        print('Пост успешно опубликован!')
        print('ID:', post['id'])
        print('URL:', post['link'])
    except Exception as e:
        print('Ошибка публикации:', e) 