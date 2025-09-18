import os
import logging
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, ContextTypes, ConversationHandler, CallbackQueryHandler, MessageHandler, filters
)
from telegram_bot_calendar import DetailedTelegramCalendar
import feedparser
from filter_news import filter_news

from database import add_keyword, get_keywords, add_category, get_categories, add_news, get_news
from newsapi import search_news

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения!")

HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME", "telegr77-6209977497ad")
WEBHOOK_URL = f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}"

NEWS_SOURCES = [
    # Великобритания
    "https://www.bbc.com/news/world/rss.xml",
    "https://www.theguardian.com/world/rss",
    "https://www.independent.co.uk/news/world/rss",
    "https://feeds.skynews.com/feeds/rss/world.xml",

    # Германия
    "https://www.spiegel.de/international/index.rss",
    "https://rss.sueddeutsche.de/rss/Politik",
    "https://www.dw.com/en/top-stories/s-9097/rss.xml",
    "https://www.tagesschau.de/xml/rss2/",

    # Франция
    "https://www.france24.com/en/rss",
    "https://www.lemonde.fr/international/rss_full.xml",
    "https://www.rfi.fr/en/rss",

    # Италия
    "https://www.ansa.it/sito/notizie/mondo/mondo_rss.xml",
    "https://www.ilpost.it/feed/",

    # Испания
    "https://english.elpais.com/rss/section/international/",
    "https://e00-elmundo.uecdn.es/elmundo/rss/internacional.xml",

    # Польша
    "https://www.tvn24.pl/najnowsze.xml",
    "https://wiadomosci.onet.pl/rss.xml",
    "https://wyborcza.pl/pub/rss/wyborcza.xml",
    "https://notesfrompoland.com/feed/",

    # Нидерланды
    "https://nltimes.nl/rss",
    "https://www.dutchnews.nl/feed/",

    # Бельгия
    "https://www.brusselstimes.com/feed/",
    "https://www.lesoir.be/rss/lesoir.xml",

    # Португалия
    "https://expresso.pt/rss/ultimas",
    "https://www.publico.pt/rss",

    # Чехия
    "https://www.seznamzpravy.cz/rss",
    "https://denikn.cz/feed/",

    # Словакия
    "https://dennikn.sk/feed/",
    "https://www.sme.sk/rss/sekcie/2/index.xml",

    # Финляндия
    "https://www.hs.fi/rss/english.xml",
    "https://yle.fi/uutiset/osasto/news/rss.xml",

    # Швеция
    "https://www.svt.se/rss.xml",
    "https://www.dn.se/rss/",

    # Дания
    "https://www.tv2.dk/rss",
    "https://politiken.dk/rss",

    # Норвегия
    "https://www.nrk.no/toppsaker.rss",
    "https://www.aftenposten.no/rss",

    # Ирландия
    "https://www.irishtimes.com/international/rss",

    # Австрия
    "https://www.derstandard.at/rss",
    "https://www.diepresse.com/rss",

    # Швейцария
    "https://www.nzz.ch/rss",
    "https://www.letemps.ch/rss",

    # Болгария
    "https://www.dnevnik.bg/rss/",
    "https://www.segabg.com/rss.xml",

    # Румыния
    "https://www.gandul.ro/rss",
    "https://www.digi24.ro/rss",

    # Греция
    "https://www.kathimerini.gr/feed/",
    "https://www.protothema.gr/rss/news-international.xml",

    # Литва, Латвия, Эстония (Балтия)
    "https://www.delfi.lt/rss/",
    "https://www.delfi.lv/rss/",
    "https://www.delfi.ee/rss/",
    "https://www.lrytas.lt/rss",
    "https://www.la.lv/feed",
    "https://www.postimees.ee/rss",

    # Хорватия
    "https://www.jutarnji.hr/rss",
    "https://www.index.hr/rss",

    # Сербия
    "https://nova.rs/feed/",
    "https://www.blic.rs/rss",
    "https://informer.rs/rss",

    # Босния и Герцеговина
    "https://www.klix.ba/rss",
    "https://www.oslobodjenje.ba/feed",

    # Черногория
    "https://www.vijesti.me/rss",

    # Словения
    "https://www.delo.si/rss/",

    # Албания
    "https://gazeta-shqip.com/feed/",

    # Северная Македония
    "https://novamakedonija.com.mk/feed/",

    # Кипр
    "https://www.philenews.com/rss/",
    "https://www.politis.com.cy/feed/",

    # Мальта
    "https://timesofmalta.com/rss",

    # Люксембург
    "https://www.wort.lu/en/rss",

    # Украина (главные англоязычные и русскоязычные ленты)
    "https://www.ukrinform.ua/rss/rss.php",
    "https://www.pravda.com.ua/eng/rss/",
    "https://www.liga.net/rss", 
    "https://censor.net/rss",
    "https://www.eurointegration.com.ua/rss.xml",
    "https://novayagazeta.eu/rss",
    "https://www.euronews.com/rss?level=theme&name=ukraine-crisis",

    # Международные (часто публикуют про Украину)
    "https://www.politico.eu/feed/",
    "https://www.eurotopics.net/en/rss.xml",
    "https://feeds.nova.bg/news/world/rss.xml",
]

PERIOD, CALENDAR_START, CALENDAR_END, KEYWORDS = range(4)

# --- Команды ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = f"https://{HEROKU_APP_NAME}.herokuapp.com/?user_id={user_id}"
    keyboard = [[InlineKeyboardButton("🌐 Перейти на сайт", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "<b>Привет!</b> Я бот для поиска и сортировки новостей по ключевым словам и категориям.\n\n"
        "Вот мои команды:\n"
        "🔑 <b>/add_keyword</b> слово категория — добавить ключевое слово\n"
        "📋 <b>/list_keywords</b> — список ваших ключевых слов\n"
        "📂 <b>/add_category</b> категория — добавить новую категорию\n"
        "🗂️ <b>/list_categories</b> — список ваших категорий\n"
        "📰 <b>/news</b> — показать новости по ключевым словам\n"
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
    await update.message.reply_text(
        f"🔑 Ключевое слово <b>{word}</b> добавлено в категорию <b>{category}</b>.", parse_mode='HTML')

async def list_keywords_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keywords = get_keywords()
    if not keywords:
        await update.message.reply_text("🔑 Ключевые слова не добавлены.")
        return
    msg = "\n".join([f"• <b>{kw['word']}</b> — {kw['category']}" for kw in keywords])
    user_id = update.effective_user.id
    url = f"https://{HEROKU_APP_NAME}.herokuapp.com/?user_id={user_id}"
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
    url = f"https://{HEROKU_APP_NAME}.herokuapp.com/?user_id={user_id}"
    keyboard = [[InlineKeyboardButton("🌐 Перейти на сайт", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"🗂️ Ваши категории:\n{msg}",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def site_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = f"https://{HEROKU_APP_NAME}.herokuapp.com/?user_id={user_id}"
    keyboard = [[InlineKeyboardButton("🌐 Перейти на сайт", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌐 Для удобного управления новостями воспользуйтесь сайтом:",
        reply_markup=reply_markup
    )

# --- Диалог поиска новостей через календарь ---
async def news_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Сегодня", callback_data="today")],
        [InlineKeyboardButton("Последние 3 дня", callback_data="3days")],
        [InlineKeyboardButton("Неделя", callback_data="week")],
        [InlineKeyboardButton("Выбрать диапазон на календаре", callback_data="calendar")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выберите период для поиска новостей:", reply_markup=reply_markup)
    return PERIOD

async def period_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data['period'] = query.data

    if query.data == "calendar":
        calendar, step = DetailedTelegramCalendar(min_date=datetime.date(2020,1,1)).build()
        await query.edit_message_text("Выберите начальную дату:", reply_markup=calendar)
        return CALENDAR_START
    else:
        await query.edit_message_text("Введите ключевые слова для поиска (через запятую):")
        return KEYWORDS

async def calendar_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result, key, step = DetailedTelegramCalendar().process(update.callback_query.data)
    if not result and key:
        await update.callback_query.edit_message_text("Выберите начальную дату:", reply_markup=key)
        return CALENDAR_START
    elif result:
        context.user_data['start_date'] = result
        calendar, step = DetailedTelegramCalendar().build()
        await update.callback_query.edit_message_text("Выберите конечную дату:", reply_markup=calendar)
        return CALENDAR_END

async def calendar_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result, key, step = DetailedTelegramCalendar().process(update.callback_query.data)
    if not result and key:
        await update.callback_query.edit_message_text("Выберите конечную дату:", reply_markup=key)
        return CALENDAR_END
    elif result:
        context.user_data['end_date'] = result
        await update.callback_query.edit_message_text("Введите ключевые слова для поиска (через запятую):")
        return KEYWORDS

async def keywords_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    keywords = [kw.strip() for kw in text.split(',') if kw.strip()]
    context.user_data['keywords'] = keywords

    period = context.user_data.get('period')
    start_date = context.user_data.get('start_date')
    end_date = context.user_data.get('end_date')

    today = datetime.datetime.now(datetime.UTC).date()
    if period == "today":
        start_date = end_date = today
    elif period == "3days":
        end_date = today
        start_date = end_date - datetime.timedelta(days=2)
    elif period == "week":
        end_date = today
        start_date = end_date - datetime.timedelta(days=6)
    # Для календаря start_date, end_date уже заданы

    news_items = get_news()
    filtered_news = filter_news(start_date, end_date, keywords, news_items)

    if not filtered_news:
        await update.message.reply_text("📰 Новости не найдены по этим параметрам.")
        return ConversationHandler.END

    for item in filtered_news[:10]:
        msg = (
            f"<b>{item['title']}</b>\n{item.get('description','')}\n"
            f"<a href=\"{item['url']}\">Читать подробнее</a>\n"
            f"Категория: {item.get('category', 'Без категории')}\n"
            f"Дата: {item.get('published_at','')}\n"
        )
        await update.message.reply_text(msg, parse_mode="HTML")
    return ConversationHandler.END

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("news", news_cmd)],
    states={
        PERIOD: [CallbackQueryHandler(period_chosen)],
        CALENDAR_START: [CallbackQueryHandler(calendar_start)],
        CALENDAR_END: [CallbackQueryHandler(calendar_end)],
        KEYWORDS: [MessageHandler(filters.TEXT & (~filters.COMMAND), keywords_chosen)],
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

    logger.info("Starting bot via webhook...")
    app.run_webhook(
        listen="0.0.0.0",
        port=int(os.environ.get("PORT", 8443)),
        url_path=TOKEN,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
