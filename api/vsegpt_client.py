import requests

class VseGPTClient:
    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url.rstrip('/')

    def generate_article(self, topic, image_urls=None):
        prompt = self._build_prompt(topic, image_urls)
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': 'openai/gpt-4.1-mini',
            'messages': [
                {'role': 'user', 'content': prompt}
            ]
        }
        r = requests.post(f'{self.api_url}/chat/completions', json=data, headers=headers)
        r.raise_for_status()
        return r.json()

    def _build_prompt(self, topic, image_urls=None):
        images = ''
        if image_urls:
            images = '\n'.join(image_urls)
        return f'''
You are an expert SEO copywriter.  
Generate a full, SEO-optimized article in English for the topic: "{topic}".  
Requirements:
- Title (h1)
- Main body (HTML formatted, with subheadings, lists, etc.)
- 3-5 relevant tags (comma separated)
- Insert provided image URLs as <img> tags in appropriate places in the article (use all images)
- The article must be at least 1500 words
- Write a short summary (max 900 characters) for Telegram, including a call to action and a link to the site, wrapped in the text "Global Vendor Network"
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