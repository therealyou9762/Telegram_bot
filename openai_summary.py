import os
import logging
import datetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, ContextTypes, ConversationHandler,
    CallbackQueryHandler, MessageHandler, filters
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import feedparser

from database import add_keyword, get_keywords, add_category, get_categories, add_news, get_news
from newsapi import search_news

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения!")

NEWS_SOURCES = [
    "https://www.ukrinform.ua/rss/rss.php",
    "https://www.bbc.com/news/world/rss.xml",
    "https://www.france24.com/en/rss",
    # Добавь другие при необходимости
]

PERIOD, KEYWORDS = range(2)

# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = f"https://telegr77-6209977497ad.herokuapp.com/?user_id={user_id}"
    keyboard = [[InlineKeyboardButton("🌐 Перейти на сайт", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "<b>Привет!</b> Я бот для поиска и сортировки новостей по ключевым словам и категориям.\n\n"
        "Вот мои команды:\n"
        "🔑 <b>/add_keyword</b> слово категория — добавить ключевое слово\n"
        "📋 <b>/list_keywords</b> — список ваших ключевых слов\n"
        "📂 <b>/add_category</b> категория — добавить новую категорию\n"
        "🗂️ <b>/list_categories</b> — список ваших категорий\n"
        "📰 <b>/news</b> слово — показать новости по ключевым словам\n"
        "🌐 <b>/site</b> — открыть сайт управления новостями\n\n"
        "Для удобного управления новостями воспользуйтесь кнопкой ниже.",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def add_keyword_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Использование: /add_keyword <слово> <категория>")
        return
    word, category = context.args[0], " ".join(context.args[1:])
    add_keyword(word, category)
    await update.message.reply_text(f"🔑 Ключевое слово <b>{word}</b> добавлено в категорию <b>{category}</b>.", parse_mode='HTML')

async def list_keywords_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keywords = get_keywords()
    if not keywords:
        await update.message.reply_text("🔑 Ключевые слова не добавлены.")
        return
    msg = "\n".join([f"• <b>{kw['word']}</b> — {kw['category']}" for kw in keywords])
    user_id = update.effective_user.id
    url = f"https://telegr77-6209977497ad.herokuapp.com/?user_id={user_id}"
    keyboard = [[InlineKeyboardButton("🌐 Перейти на сайт", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"📋 Ваши ключевые слова:\n{msg}",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def add_category_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /add_category <категория>")
        return
    name = " ".join(context.args)
    add_category(name)
    await update.message.reply_text(f"📂 Категория <b>{name}</b> добавлена.", parse_mode='HTML')

async def list_categories_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = get_categories()
    if not categories:
        await update.message.reply_text("🗂️ Категории не добавлены.")
        return
    msg = "\n".join([f"• <b>{cat['name']}</b>" for cat in categories])
    user_id = update.effective_user.id
    url = f"https://telegr77-6209977497ad.herokuapp.com/?user_id={user_id}"
    keyboard = [[InlineKeyboardButton("🌐 Перейти на сайт", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"🗂️ Ваши категории:\n{msg}",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def site_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = f"https://telegr77-6209977497ad.herokuapp.com/?user_id={user_id}"
    keyboard = [[InlineKeyboardButton("🌐 Перейти на сайт", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌐 Для удобного управления новостями воспользуйтесь сайтом:",
        reply_markup=reply_markup
    )

# --- Диалог поиска новостей ---
async def news_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Сегодня", callback_data="today")],
        [InlineKeyboardButton("Последние 3 дня", callback_data="3days")],
        [InlineKeyboardButton("Неделя", callback_data="week")],
        [InlineKeyboardButton("Указать диапазон", callback_data="custom")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите период для поиска новостей:", reply_markup=reply_markup)
    return PERIOD

async def period_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['period'] = query.data

    if query.data == "custom":
        await query.edit_message_text("Введите диапазон дат в формате ГГГГ-ММ-ДД - ГГГГ-ММ-ДД (например, 2025-09-10 - 2025-09-17):")
        return PERIOD
    else:
        await query.edit_message_text("Введите ключевые слова для поиска (через запятую):")
        return KEYWORDS

async def custom_period(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        start_str, end_str = map(str.strip, text.split('-'))
        start_date = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
        end_date = datetime.datetime.strptime(end_str, "%Y-%m-%d").date()
        context.user_data['custom_range'] = (start_date, end_date)
        await update.message.reply_text("Введите ключевые слова для поиска (через запятую):")
        return KEYWORDS
    except Exception:
        await update.message.reply_text("Ошибка! Введите диапазон дат корректно (например, 2025-09-10 - 2025-09-17):")
        return PERIOD

async def keywords_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    keywords = [kw.strip() for kw in text.split(',') if kw.strip()]
    context.user_data['keywords'] = keywords

    period = context.user_data.get('period')
    custom_range = context.user_data.get('custom_range')

    start_date, end_date = get_period_dates(period, custom_range)
    news_items = filter_news(start_date, end_date, keywords)

    if not news_items:
        await update.message.reply_text("📰 Новости не найдены по этим параметрам.")
        return ConversationHandler.END

    for item in news_items[:10]:  # выводим максимум 10 новостей
        msg = (
            f"<b>{item['title']}</b>\n{item.get('description','')}\n"
            f"<a href=\"{item['url']}\">Читать подробнее</a>\n"
            f"Категория: {item.get('category', 'Без категории')}\n"
            f"Дата: {item.get('published_at','')}\n"
        )
        await update.message.reply_text(msg, parse_mode="HTML")
    return ConversationHandler.END

def get_period_dates(period, custom_range=None):
    today = datetime.datetime.utcnow().date()
    if period == "today":
        return today, today
    elif period == "3days":
        return today - datetime.timedelta(days=2), today
    elif period == "week":
        return today - datetime.timedelta(days=6), today
    elif period == "custom" and custom_range:
        return custom_range
    else:
        return today, today

def filter_news(start_date, end_date, keywords):
    # Здесь берем все новости из БД (или любого источника)
    result = []
    for news in get_news():  # get_news должен возвращать список словарей новостей
        try:
            pub_dt = news.get('published_at', '')
            if isinstance(pub_dt, str):
                pub_dt = datetime.datetime.strptime(pub_dt[:10], "%Y-%m-%d").date()
            if start_date <= pub_dt <= end_date and any(kw.lower() in (news.get('title','')+news.get('description','')).lower() for kw in keywords):
                result.append(news)
        except Exception:
            continue
    return result

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("news", news_cmd)],
    states={
        PERIOD: [
            CallbackQueryHandler(period_chosen),
            MessageHandler(filters.TEXT & (~filters.COMMAND), custom_period)
        ],
        KEYWORDS: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), keywords_chosen)
        ],
    },
    fallbacks=[],
)

# --- Автоматический сбор новостей каждый час ---
async def scheduled_news_job(context):
    kw_list = [kw['word'] for kw in get_keywords()]
    all_news = search_news(kw_list)
    for src in NEWS_SOURCES:
        feed = feedparser.parse(src)
        for entry in feed.entries:
            for kw in kw_list:
                if kw.lower() in (entry.title + entry.get('summary', '')).lower():
                    news_item = {
                        "title": entry.title,
                        "url": entry.link,
                        "description": entry.get("summary", ""),
                        "category": entry.get("category", "Без категории"),
                        "published_at": entry.get("published", ""),
                    }
                    add_news(
                        news_item['title'],
                        news_item['url'],
                        news_item.get('description', ''),
                        news_item.get('category', 'Без категории'),
                        news_item['published_at']
                    )
                    break

async def start_news_scheduler(application):
    application.job_queue.run_repeating(scheduled_news_job, interval=3600, first=0)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_keyword", add_keyword_cmd))
    app.add_handler(CommandHandler("list_keywords", list_keywords_cmd))
    app.add_handler(CommandHandler("add_category", add_category_cmd))
    app.add_handler(CommandHandler("list_categories", list_categories_cmd))
    app.add_handler(CommandHandler("site", site_cmd))
    app.add_handler(conv_handler)
    app.post_init = start_news_scheduler
    logger.info("Starting bot polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
