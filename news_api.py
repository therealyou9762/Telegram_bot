import redis
import json
import os

redis_client = redis.from_url(os.getenv('REDIS_URL'))

def fetch_news_from_api(keywords, language='ru', country='ru', sources=None):
    cache_key = f"news:{keywords}:{language}:{country}"
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    # ... rest is the same as above (Webz.io call) ...
    articles = ... # result of API call
    redis_client.setex(cache_key, 900, json.dumps(articles))  # cache for 15 min
    return articles
