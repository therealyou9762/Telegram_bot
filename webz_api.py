import os
import requests

WEBZ_API_KEY = os.getenv("WEBZ_API_KEY")

def search_news(keywords, language='ru', size=5):
    # keywords: список строк
    query = ' OR '.join(keywords)
    url = f"https://api.webz.io/newsApiLite?token={WEBZ_API_KEY}&q={query}&language={language}&size={size}"
    resp = requests.get(url)
    if resp.status_code != 200:
        raise Exception(f"Webz.io error: {resp.text}")
    data = resp.json()
    result_news = []
    for item in data.get("articles", []):
        result_news.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "summary": item.get("summary", ""),
            "published_at": item.get("published", ""),
        })
    return result_news
