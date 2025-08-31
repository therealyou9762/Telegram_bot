import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import Config
from database import get_user, update_user, add_to_array, remove_from_array, update_stats, init_db, get_db_connection
from news_api import fetch_news_from_api
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()


async def check_news_for_user(user_id, application):
    """Проверка новостей для конкретного пользователя"""
    try:
        user = get_user(user_id)
        if not user or not user['keywords']:
            return

        articles = fetch_news_from_api(
            user['keywords'],
            user['language'],
            user['country']
        )

        for article in articles:
            title = article['title'].lower()
            content = (article.get('description') or '').lower()
            full_text = f"{title} {content}"

            # Проверка черного списка
            if any(black_word in full_text for black_word in user['blacklist']):
                continue

            # Проверка ключевых слов
            is_priority = any(p_keyword.lower() in full_text for p_keyword in user['priority_keywords'])
            has_keyword = any(keyword.lower() in full_text for keyword in user['keywords'])

            if has_keyword or is_priority:
                # Генерация summary для приоритетных новостей
                summary = ""
                # if is_priority and Config.OPENAI_API_KEY:
                #     news_text = f"{article['title']}\n\n{article.get('description', '')}"
                #     summary = generate_summary(news_text)

                message = f"{'🚨 ' if is_priority else ''}*{article['title']}*\n"
                if summary:
                    message += f"\n{summary}\n"
                message += f"\n{article['url']}"

                try:
                    await application.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    # Обновление статистики
                    for keyword in user['keywords']:
                        if keyword.lower() in full_text:
                            update_stats(user_id, keyword)

                    await asyncio.sleep(1)  # Задержка между сообщениями
                except Exception as e:
                    logger.error(f"Error sending message to {user_id}: {e}")

    except Exception as e:
        logger.error(f"Error checking news for user {user_id}: {e}")


async def scheduled_news_check(application):
    """Запланированная проверка новостей для всех пользователей"""
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM users")
            users = cursor.fetchall()

    for (user_id,) in users:
        await check_news_for_user(user_id, application)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    user = get_user(user_id)

    if not user:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (user_id, username) VALUES (%s, %s)",
            (user_id, update.effective_user.username)
        )
        conn.commit()
        cursor.close()
        conn.close()

    welcome_text = """
    Привет! Я бот для отбора новостей. 🗞️

    Доступные команды:
    /add_keyword - добавить ключевое слово
    /add_priority - добавить приоритетное слово
    /add_source - добавить источник
    /blacklist - добавить в черный список
    /settings - настройки
    /stats - статистика

    Настройте бота через веб-интерфейс: [ваш-сайт]/settings
    """

    await update.message.reply_text(welcome_text)


async def add_keyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление ключевого слова"""
    if not context.args:
        await update.message.reply_text("Укажите ключевое слово: /add_keyword слово")
        return

    keyword = ' '.join(context.args)
    user_id = update.effective_user.id
    add_to_array(user_id, 'keywords', keyword)
    await update.message.reply_text(f"Ключевое слово добавлено: {keyword}")


# Аналогично реализуйте другие команды: add_priority, add_source, blacklist, etc.

def setup_scheduler(application):
    """Настройка планировщика"""
    trigger = IntervalTrigger(hours=1)
    scheduler.add_job(
        lambda: asyncio.run(scheduled_news_check(application)),
        trigger,
        id='news_check'
    )
    scheduler.start()


def main():
    """Основная функция"""

    # Инициализация БД
    init_db()

    # Создание приложения Telegram
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

    # Добавление обработчиков команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("add_keyword", add_keyword))
    # Добавьте другие обработчики...

    # Настройка планировщика
    setup_scheduler(application)

    # Запуск бота
    application.run_polling()


if __name__ == '__main__':
    main()