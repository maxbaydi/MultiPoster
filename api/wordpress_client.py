import requests
from requests.auth import HTTPBasicAuth

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "DNT": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1"
}

class WordPressClient:
    def __init__(self, url, username, app_password):
        self.url = url.rstrip('/')
        self.auth = HTTPBasicAuth(username, app_password)

    def test_connection(self):
        r = requests.get(f'https://{self.url}/wp-json/wp/v2/posts', auth=self.auth, headers=BROWSER_HEADERS)
        return r.status_code == 200

    def upload_media(self, file_path):
        with open(file_path, 'rb') as f:
            filename = file_path.split('/')[-1]
            headers = BROWSER_HEADERS.copy()
            headers['Content-Disposition'] = f'attachment; filename={filename}'
            r = requests.post(
                f'https://{self.url}/wp-json/wp/v2/media',
                headers=headers,
                files={'file': (filename, f)},
                auth=self.auth
            )
        if r.status_code in (200, 201):
            return r.json()['id'], r.json()['source_url']
        else:
            raise Exception(f'Upload failed: {r.text}')

    def create_post(self, title, content, status='publish', tags=None, media_ids=None, category_id=None):
        data = {
            'title': title,
            'content': content,
            'status': status,
        }
        if tags:
            data['tags'] = tags
        if media_ids:
            data['featured_media'] = media_ids[0] if isinstance(media_ids, list) else media_ids
        if category_id:
            data['categories'] = [category_id]
        headers = BROWSER_HEADERS.copy()
        headers['Content-Type'] = 'application/json'
        r = requests.post(
            f'https://{self.url}/wp-json/wp/v2/posts',
            json=data,
            auth=self.auth,
            headers=headers
        )
        if r.status_code in (200, 201):
            return r.json()
        else:
            raise Exception(f'Post creation failed: {r.text}')

    def get_categories(self):
        headers = BROWSER_HEADERS.copy()
        r = requests.get(
            f'https://{self.url}/wp-json/wp/v2/categories?per_page=100',
            auth=self.auth,
            headers=headers
        )
        if r.status_code == 200:
            return r.json()
        else:
            raise Exception(f'Failed to fetch categories: {r.text}') 