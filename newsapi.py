import os
import requests

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")  # Добавь ключ в переменные окружения!

def search_news(keywords, language='ru', limit=5):
    if not NEWS_API_KEY:
        raise Exception("TheNewsAPI ключ не найден.")
    if isinstance(keywords, list):
        keywords = " ".join(keywords)
    url = (
        f"https://api.thenewsapi.com/v1/news/all"
        f"?api_token={NEWS_API_KEY}"
        f"&language={language}"
        f"&search={keywords}"
        f"&limit={limit}"
    )
    resp = requests.get(url, timeout=20)
    if resp.status_code != 200:
        raise Exception(f"TheNewsAPI error: {resp.text}")
    data = resp.json()
    articles = data.get("data", [])
    return [
        {
            "title": a.get("title"),
            "url": a.get("url"),
            "published_at": a.get("published_at"),
            "description": a.get("description"),
            "source": a.get("source"),
        }
        for a in articles
    ]
