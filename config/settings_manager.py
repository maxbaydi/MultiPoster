import json
import os

class SettingsManager:
    def __init__(self, path='settings.json'):
        self.path = path
        self.data = {
            "telegram_bots": [],
            "wordpress_sites": [],
            "vsegpt": {"api_key": "", "url": ""}
        }
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, 'r', encoding='utf-8') as f:
                    self.data = json.load(f)
            except Exception:
                pass

    def save(self):
        with open(self.path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def get_telegram_bots(self):
        return self.data.get('telegram_bots', [])

    def set_telegram_bots(self, bots):
        self.data['telegram_bots'] = bots
        self.save()

    def get_wordpress_sites(self):
        return self.data.get('wordpress_sites', [])

    def set_wordpress_sites(self, sites):
        self.data['wordpress_sites'] = sites
        self.save()

    def get_vsegpt(self):
        return self.data.get('vsegpt', {})

    def set_vsegpt(self, vsegpt):
        self.data['vsegpt'] = vsegpt
        self.save()
