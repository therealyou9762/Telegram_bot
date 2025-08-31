import requests
from config import Config


def fetch_news_from_api(keywords, language='ru', country='ru', sources=None):
    """Получение новостей через NewsAPI"""
    url = 'https://newsapi.org/v2/top-headlines'

    params = {
        'q': ' '.join(keywords) if isinstance(keywords, list) else keywords,
        'language': language,
        'country': country,
        'apiKey': Config.NEWS_API_KEY,
        'pageSize': 20
    }

    if sources:
        params['sources'] = ','.join(sources) if isinstance(sources, list) else sources

    if not Config.NEWS_API_KEY:
        print("NewsAPI key is missing.")
        return []

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        if data.get('status') == 'ok':
            return data.get('articles', [])
        else:
            print(f"NewsAPI error: {data.get('message')}")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return []