from config.env_manager import EnvManager
from api.wordpress_client import WordPressClient
from api.telegram_client import TelegramClient
from api.vsegpt_client import VseGPTClient

if __name__ == '__main__':
    env = EnvManager()
    print('--- ENV ---')
    print(env.all())
    print('--- WordPress ---')
    wp = WordPressClient(env.get('WP_URL'), env.get('WP_USERNAME'), env.get('WP_APP_PASSWORD'))
    print('WordPress connection:', wp.test_connection())

    print('--- Telegram ---')
    tg = TelegramClient(env.get('TELEGRAM_BOT_TOKEN'), env.get('TELEGRAM_CHANNEL_ID'))
    resp = tg.send_message('Test message from MultiPoster!')
    print('Telegram response:', resp)

    print('--- VseGPT ---')
    gpt = VseGPTClient(env.get('VSEGPT_API_KEY'), env.get('VSEGPT_URL'))
    resp = gpt.generate_article('Test topic')
    print('VseGPT response:', resp) 