from news_domains import EU_NEWS_DOMAINS
from translate_utils import translate_keywords
from datetime import datetime

def filter_news(start_date, end_date, keywords, news_items):
    translations = []
    for kw in keywords:
        translations.extend(translate_keywords(kw).values())
    results = []
    for news in news_items:
        # Преобразуем дату публикации в объект date
        pub_date_str = news.get('published_at', '')
        try:
            pub_date = datetime.strptime(pub_date_str, "%Y-%m-%d").date()
        except ValueError:
            continue  # если дата невалидна, пропускаем

        if start_date <= pub_date <= end_date:
            if any(domain in news['url'] for domain in EU_NEWS_DOMAINS):
                if any(trans.lower() in (news.get('title','') + news.get('description','')).lower() for trans in translations):
                    results.append(news)
    return results
