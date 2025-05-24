import requests

class TelegramClient:
    def __init__(self, bot_token, channel_id):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.api_url = f'https://api.telegram.org/bot{self.bot_token}'

    def send_message(self, text, parse_mode='HTML', disable_web_page_preview=False):
        data = {
            'chat_id': self.channel_id,
            'text': text,
            'parse_mode': parse_mode,
            'disable_web_page_preview': disable_web_page_preview
        }
        r = requests.post(f'{self.api_url}/sendMessage', data=data)
        return r.json()

    def send_photo(self, photo_path, caption=None, parse_mode='HTML'):
        with open(photo_path, 'rb') as f:
            files = {'photo': f}
            data = {'chat_id': self.channel_id}
            if caption:
                data['caption'] = caption
                data['parse_mode'] = parse_mode
            r = requests.post(f'{self.api_url}/sendPhoto', data=data, files=files)
        return r.json() 