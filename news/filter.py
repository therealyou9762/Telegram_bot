import datetime

def filter_news(start_date, end_date, keywords, news_items):
    """Фильтрует новости по дате и ключевым словам."""
    result = []
    for item in news_items:
        pub_date = item.get('published_at')
        if isinstance(pub_date, str):
            pub_date = datetime.datetime.strptime(pub_date, "%Y-%m-%d").date()
        elif isinstance(pub_date, datetime.datetime):
            pub_date = pub_date.date()
        if pub_date:
            if not (start_date <= pub_date <= end_date):
                continue
        if keywords:
            text = (item.get('title', '') + item.get('summary', '')).lower()
            if not any(kw.lower() in text for kw in keywords):
                continue
        result.append(item)
    return result
