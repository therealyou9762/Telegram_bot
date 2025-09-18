from news_domains import EU_NEWS_DOMAINS
from translate_utils import translate_keywords

def filter_news(start_date, end_date, keywords, news_items):
    translations = []
    for kw in keywords:
        translations.extend(translate_keywords(kw).values())
    results = []
    for news in news_items:
        if any(domain in news['url'] for domain in EU_NEWS_DOMAINS):
            if any(trans.lower() in (news.get('title','') + news.get('description','')).lower() for trans in translations):
                # фильтрация по датам, если нужно
                results.append(news)
    return results
