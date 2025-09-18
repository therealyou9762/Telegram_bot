import os
import requests
import datetime

WEBZ_API_KEY = os.getenv("WEBZ_API_KEY")

def search_news(keywords):
    """Возвращает новости, найденные по ключевым словам через Webz API."""
    if not WEBZ_API_KEY or not keywords:
        return []
    results = []
    for kw in keywords:
        url = "https://api.webz.io/newsApiLite"
        params = {
            "token": WEBZ_API_KEY,
            "q": kw,
            "language": "en",
            "size": 10,
        }
        try:
            resp = requests.get(url, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            news = data.get("articles", [])
            # Приведение даты к datetime
            for n in news:
                if 'published' in n:
                    try:
                        n['published_at'] = datetime.datetime.strptime(n['published'], "%Y-%m-%dT%H:%M:%SZ")
                    except Exception:
                        n['published_at'] = None
            results.extend(news)
        except Exception as e:
            print(f"Error fetching news: {e}")
    return results
