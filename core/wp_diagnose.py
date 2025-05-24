import requests
import json
from config.env_manager import EnvManager

if __name__ == '__main__':
    env = EnvManager()
    WORDPRESS_URL = f"https://{env.get('WP_URL')}"
    USERNAME = env.get('WP_USERNAME')
    APPLICATION_PASSWORD = env.get('WP_APP_PASSWORD')
    API_BASE_URL = f"{WORDPRESS_URL}/wp-json/wp/v2/posts"

    auth_headers = requests.auth.HTTPBasicAuth(USERNAME, APPLICATION_PASSWORD)
    browser_headers = {
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

    def handle_response(response):
        print(f"Статус: {response.status_code}")
        try:
            data = response.json()
            print("Ответ JSON:", json.dumps(data, indent=2, ensure_ascii=False))
        except Exception:
            print("Ответ не JSON:", response.text)
        return response

    print("\n--- Получение всех постов (browser headers) ---")
    try:
        response = requests.get(API_BASE_URL, auth=auth_headers, headers=browser_headers)
        handle_response(response)
    except requests.exceptions.RequestException as e:
        print(f"Произошла ошибка при запросе: {e}") 