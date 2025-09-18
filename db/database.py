from db.models import db, Keyword, Category, News, NewsStat
from sqlalchemy import func
import datetime

# --- Категории ---
def add_category(name):
    category = Category.query.filter_by(name=name).first()
    if not category:
        category = Category(name=name)
        db.session.add(category)
        db.session.commit()
    return category.id

def get_categories():
    return [{'id': cat.id, 'name': cat.name} for cat in Category.query.order_by(Category.name.asc()).all()]

# --- Ключевые слова ---
def add_keyword(word, category_name):
    category_id = add_category(category_name)
    kw = Keyword(word=word, category_id=category_id)
    db.session.add(kw)
    db.session.commit()
    return kw.id

def get_keywords():
    return [
        {'word': kw.word, 'category': kw.category.name}
        for kw in Keyword.query.join(Category).order_by(Keyword.word.asc()).all()
    ]

# --- Новости ---
def add_news(title, url, summary, category_name, published_at):
    category_id = add_category(category_name)
    news = News(title=title, url=url, summary=summary, category_id=category_id, published_at=published_at)
    db.session.add(news)
    db.session.commit()

def get_news(category_name=None):
    query = News.query.join(Category)
    if category_name:
        query = query.filter(Category.name == category_name)
    return [
        {
            'title': n.title,
            'url': n.url,
            'summary': n.summary,
            'category': n.category.name if n.category else None,
            'published_at': n.published_at,
        }
        for n in query.order_by(News.published_at.desc()).all()
    ]

# --- Статистика новостей ---
def add_news_stat(user_id, keyword, source, found_count, date):
    stat = NewsStat(user_id=user_id, keyword=keyword, source=source, found_count=found_count, date=date)
    db.session.add(stat)
    db.session.commit()

def get_news_stats(user_id=None, days=7):
    query = NewsStat.query
    if user_id:
        query = query.filter(NewsStat.user_id == user_id)
    date_limit = datetime.datetime.utcnow() - datetime.timedelta(days=days)
    query = query.filter(NewsStat.date > date_limit)
    stats = query.with_entities(
        NewsStat.keyword,
        NewsStat.source,
        func.sum(NewsStat.found_count).label('total'),
        NewsStat.date
    ).group_by(NewsStat.keyword, NewsStat.source, NewsStat.date).order_by(NewsStat.date.desc())
    return [
        {
            'keyword': s.keyword,
            'source': s.source,
            'total': s.total,
            'date': s.date
        } for s in stats
    ]
