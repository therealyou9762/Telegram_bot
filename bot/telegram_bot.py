import telebot
from models import User, db

TOKEN = 'ВАШ_ТОКЕН_ТЕЛЕГРАМ'
bot = telebot.TeleBot(TOKEN)

# Пример настройки SQLAlchemy (Flask не обязателен, но часто используется)
from flask import Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://<user>:<password>@<host>:<port>/<dbname>'
db.init_app(app)

with app.app_context():
    db.create_all()  # создаёт таблицы, если их нет

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username

    with app.app_context():
        user = User.query.filter_by(id=user_id).first()
        if not user:
            user = User(id=user_id, name=name, username=username)
            db.session.add(user)
            try:
                db.session.commit()
                bot.send_message(message.chat.id, "Вы зарегистрированы!")
            except Exception as e:
                db.session.rollback()
                bot.send_message(message.chat.id, f"Ошибка при регистрации: {e}")
        else:
            bot.send_message(message.chat.id, "Вы уже зарегистрированы.")

bot.polling(none_stop=True)
from telegram.ext import Application, CommandHandler

async def start(update, context):
    await update.message.reply_text('Бот работает!')

app = Application.builder().token("ВАШ_ТОКЕН").build()
app.add_handler(CommandHandler("start", start))

if __name__ == '__main__':
    app.run_polling()
import os
import requests
import redis
import hashlib
import json

WEBZ_API_KEY = os.getenv("WEBZ_API_KEY")
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
import asyncio
from aiogram import Bot

async def send_telegram_notification(bot_token, chat_id, message):
    bot = Bot(token=bot_token)
    try:
        await bot.send_message(chat_id=chat_id, text=message)
    finally:
        await bot.session.close()

def notify_in_background(bot_token, chat_id, message, loop=None):
    loop = loop or asyncio.get_event_loop()
    loop.create_task(send_telegram_notification(bot_token, chat_id, message))
