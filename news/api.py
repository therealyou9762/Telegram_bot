import os
import requests
import redis
import hashlib
import json

WEBZ_API_KEY = os.getenv("WEBZ_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
REDIS_URL = os.getenv("REDIS_URL")

redis_client = redis.Redis.from_url(REDIS_URL) if REDIS_URL else None

def get_cached_news(query, cache_time=600):
    if not redis_client:
        return None
    key = f"news:{hashlib.sha256(query.encode()).hexdigest()}"
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None

def set_cached_news(query, news, cache_time=600):
    if not redis_client:
        return
    key = f"news:{hashlib.sha256(query.encode()).hexdigest()}"
    redis_client.setex(key, cache_time, json.dumps(news))

def fetch_news(query: str, language: str = "en", page: int = 1):
    """Fetch news using Webz.io API"""
    if not WEBZ_API_KEY:
        raise ValueError("WEBZ_API_KEY not set in environment")

    cached = get_cached_news(query)
    if cached:
        return cached

    url = "https://api.webz.io/newsApiLite"
    params = {
        "token": WEBZ_API_KEY,
        "q": query,
        "language": language,
        "size": 10,
        "from": page,
    }
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        news = data.get("articles", [])
        set_cached_news(query, news)
        return news
    except Exception as e:
        # log the error (implement your logging here)
        print(f"Error fetching news: {e}")
        return []

def search_news(keywords, language='ru', limit=5):
    """Search news using TheNewsAPI"""
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