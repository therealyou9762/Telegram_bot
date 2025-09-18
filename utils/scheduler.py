from apscheduler.schedulers.background import BackgroundScheduler
from rss_fetcher import fetch_and_filter_news

def start_news_scheduler():
    scheduler = BackgroundScheduler()
    # user_id можно получить из контекста или запускать для всех пользователей
    scheduler.add_job(lambda: fetch_and_filter_news(user_id=1), 'interval', hours=1)
    scheduler.start()
