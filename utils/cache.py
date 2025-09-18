import os
import redis
import hashlib
import json

REDIS_URL = os.getenv("REDIS_URL")
redis_client = redis.Redis.from_url(REDIS_URL) if REDIS_URL else None

def get_cached(key, cache_time=600):
    if not redis_client:
        return None
    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None

def set_cached(key, value, cache_time=600):
    if not redis_client:
        return
    redis_client.setex(key, cache_time, json.dumps(value))

def make_cache_key(prefix, value):
    return f"{prefix}:{hashlib.sha256(str(value).encode()).hexdigest()}"
