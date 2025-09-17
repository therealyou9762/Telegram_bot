import feedparser
from database import add_news, add_news_stat, get_keywords

NEWS_SOURCES = [
    "https://www.ukrinform.ua/rss/rss.php",
    "https://www.bbc.com/news/world/rss.xml",
    "https://www.france24.com/en/rss",
    # дополни по желанию
]

def fetch_and_filter_news(user_id):
    keywords = [kw['word'] for kw in get_keywords()]
    stats = []
    for src in NEWS_SOURCES:
        feed = feedparser.parse(src)
        for kw in keywords:
            matched = [entry for entry in feed.entries if kw.lower() in (entry.title + entry.summary).lower()]
            for entry in matched:
                add_news(
                    entry.title,
                    entry.link,
                    entry.summary if hasattr(entry, 'summary') else '',
                    entry.get('category', 'Без категории'),
                    entry.published if hasattr(entry, 'published') else ''
                )
            stats.append({
                "keyword": kw,
                "source": src,
                "found_count": len(matched),
                "date": entry.published[:10] if hasattr(entry, 'published') else '',
            })
    # Сохраняем статистику
    for stat in stats:
        add_news_stat(user_id, stat['keyword'], stat['source'], stat['found_count'], stat['date'])
