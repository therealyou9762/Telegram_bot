import logging
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters, ContextTypes
import feedparser
import apscheduler.schedulers.background
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import pytz
from config import Config

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# ========== БАЗА ДАННЫХ ==========
def init_db():
    with sqlite3.connect('news_bot.db') as conn:
        cursor = conn.cursor()
        # Таблица пользователей
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                sources TEXT,
                keywords TEXT,
                priority_keywords TEXT,
                blacklist TEXT,
                language TEXT,
                country TEXT,
                interval INTEGER
            )
        ''')
        # Таблица статистики
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                date TEXT,
                keyword TEXT,
                count INTEGER,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        conn.commit()


def get_user(user_id):
    with sqlite3.connect('news_bot.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
    if user:
        # user_id, sources, keywords, priority_keywords, blacklist, language, country, interval
        return {
            'user_id': user[0],
            'sources': user[1].split(';') if user[1] else [],
            'keywords': user[2].split(';') if user[2] else [],
            'priority_keywords': user[3].split(';') if user[3] else [],
            'blacklist': user[4].split(';') if user[4] else [],
            'language': user[5],
            'country': user[6],
            'interval': user[7] or 3600
        }
    return None


def update_user(user_id, field, value):
    with sqlite3.connect('news_bot.db') as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
        conn.commit()


# ========== ОБРАБОТКА RSS ==========
def parse_rss(feed_url, keywords, priority_keywords, blacklist):
    news = []
    feed = feedparser.parse(feed_url)
    for entry in feed.entries:
        title = entry.title.lower()
        link = entry.link
        summary = entry.get('summary', '')
        content = title + " " + summary.lower()

        # Проверка черного списка
        if any(black_word in content for black_word in blacklist):
            continue

        # Проверка на приоритетные ключевые слова
        is_priority = any(p_keyword.lower() in content for p_keyword in priority_keywords)

        # Проверка на обычные ключевые слова
        if any(keyword.lower() in content for keyword in keywords) or is_priority:
            news.append({
                'title': entry.title,
                'link': link,
                'priority': is_priority
            })
    return news


# ========== ЗАПЛАНИРОВАННАЯ ПРОВЕРКА ==========
async def scheduled_news_check(context: ContextTypes.DEFAULT_TYPE):
    logger.info("Запуск плановой проверки новостей")
    conn = sqlite3.connect('news_bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()

    for (user_id,) in users:
        user = get_user(user_id)
        if not user:
            continue
        all_news = []
        for source in user['sources']:
            news = parse_rss(source, user['keywords'], user['priority_keywords'], user['blacklist'])
            all_news.extend(news)

        # Отправка новостей пользователю
        for item in all_news:
            message = f"{'🚨 ' if item['priority'] else ''}{item['title']}\n{item['link']}"
            try:
                await context.bot.send_message(chat_id=user_id, text=message)
            except Exception as e:
                logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {e}")

        # Здесь можно обновлять статистику


# ========== КОМАНДЫ ТЕЛЕГРАМ-БОТА ==========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    if not user:
        conn = sqlite3.connect('news_bot.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (user_id, sources, keywords, priority_keywords, blacklist, language, country, interval) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, "", "", "", "", "ru", "ru", 3600)
        )
        conn.commit()
        conn.close()
    await update.message.reply_text(
        "Привет! Я бот для отбора новостей. Используй команды:\n"
        "/add_source <RSS-ссылка> - добавить источник\n"
        "/add_keyword <ключевое слово> - добавить ключевое слово\n"
        "/add_priority <слово> - добавить приоритетное слово\n"
        "/blacklist <слово или домен> - добавить в черный список\n"
        "/stats - показать статистику"
    )


async def add_source(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not context.args:
        await update.message.reply_text("Укажите RSS-ссылку: /add_source <url>")
        return
    new_source = context.args[0]
    user = get_user(user_id)
    current_sources = user['sources'] if user else []
    if new_source in current_sources:
        await update.message.reply_text("Этот источник уже добавлен.")
        return
    current_sources.append(new_source)
    update_user(user_id, 'sources', ';'.join(current_sources))
    await update.message.reply_text(f"Источник добавлен: {new_source}")


# Аналогично реализуй add_keyword, add_priority, blacklist, stats

# ========== ЗАПУСК И ПЛАНИРОВЩИК ==========
def main():
    init_db()
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

    # Добавление обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_source", add_source))
    # application.add_handler(CommandHandler("add_keyword", add_keyword))
    # application.add_handler(CommandHandler("add_priority", add_priority))
    # application.add_handler(CommandHandler("blacklist", blacklist))
    # application.add_handler(CommandHandler("stats", stats))

    # Настройка планировщика
    scheduler = apscheduler.schedulers.background.BackgroundScheduler()
    trigger = IntervalTrigger(hours=1)  # Проверка каждый час
    scheduler.add_job(
        scheduled_news_check,
        trigger=trigger,
        args=[application]
    )
    scheduler.start()

    application.run_polling()


if __name__ == '__main__':
    main()