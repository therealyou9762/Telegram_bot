import os
import logging
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from database import add_keyword, get_keywords, add_category, get_categories, add_news, get_news
from newsapi import search_news

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения!")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

async def news_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        kw_list = context.args if context.args else ["Россия"]
        news_list = search_news(kw_list)
        if not news_list:
            await update.message.reply_text("📰 Новости не найдены.")
            return

        for news in news_list:
            add_news(
                news['title'],
                news['url'],
                news.get('description', ''),
                news.get('category', 'Без категории'),
                news['published_at']
            )
            message = (
                f"<b>{news['title']}</b>\n"
                f"{news.get('description', '')}\n"
                f"<a href=\"{news['url']}\">Читать подробнее</a>\n"
                f"Категория: {news.get('category', 'Без категории')}\n"
                f"Дата: {news['published_at']}\n"
            )
            await update.message.reply_text(message, parse_mode='HTML')

    except Exception as e:
        logger.exception("Ошибка в news_cmd")
        await update.message.reply_text(f"Ошибка при получении новостей: {e}")

async def site_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = f"https://telegr77-6209977497ad.herokuapp.com/?user_id={user_id}"
    keyboard = [[InlineKeyboardButton("🌐 Перейти на сайт", url=url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🌐 Для удобного управления новостями воспользуйтесь сайтом:",
        reply_markup=reply_markup
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_keyword", add_keyword_cmd))
    app.add_handler(CommandHandler("list_keywords", list_keywords_cmd))
    app.add_handler(CommandHandler("add_category", add_category_cmd))
    app.add_handler(CommandHandler("list_categories", list_categories_cmd))
    app.add_handler(CommandHandler("news", news_cmd))
    app.add_handler(CommandHandler("site", site_cmd))
    logger.info("Starting bot polling...")
    app.run_polling()

if __name__ == "__main__":
    main()
