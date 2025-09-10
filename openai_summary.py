import os
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
from database import add_keyword, get_keywords, add_category, get_categories, add_news, get_news
from webz_api import search_news

TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для поиска и сортировки новостей по ключевым словам и категориям.\n"
        "Используй /add_keyword, /get_news, /list_keywords, /list_categories."
    )

async def add_keyword_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Использование: /add_keyword <ключевое_слово> <категория>")
        return
    word, category = context.args[0], " ".join(context.args[1:])
    add_keyword(word, category)
    await update.message.reply_text(f"Ключевое слово '{word}' добавлено в категорию '{category}'.")

async def list_keywords_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keywords = get_keywords()
    if not keywords:
        await update.message.reply_text("Ключевые слова не добавлены.")
        return
    msg = "\n".join([f"{kw['word']} — {kw['category']}" for kw in keywords])
    await update.message.reply_text("Ключевые слова:\n" + msg)

async def add_category_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Использование: /add_category <категория>")
        return
    name = " ".join(context.args)
    add_category(name)
    await update.message.reply_text(f"Категория '{name}' добавлена.")

async def list_categories_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    categories = get_categories()
    if not categories:
        await update.message.reply_text("Категории не добавлены.")
        return
    msg = "\n".join([cat['name'] for cat in categories])
    await update.message.reply_text("Категории:\n" + msg)

async def get_news_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keywords = get_keywords()
    if not keywords:
        await update.message.reply_text("Ключевые слова не заданы.")
        return
    kw_list = [kw['word'] for kw in keywords]
    news_list = search_news(kw_list)
    if not news_list:
        await update.message.reply_text("Новостей не найдено.")
        return
    for news in news_list:
        add_news(news['title'], news['url'], news['summary'], news.get('category', 'Без категории'), news['published_at'])
        msg = f"📰 <b>{news['title']}</b>\n{news['summary']}\n<a href='{news['url']}'>Читать полностью</a>"
        await update.message.reply_html(msg)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_keyword", add_keyword_cmd))
    app.add_handler(CommandHandler("list_keywords", list_keywords_cmd))
    app.add_handler(CommandHandler("add_category", add_category_cmd))
    app.add_handler(CommandHandler("list_categories", list_categories_cmd))
    app.add_handler(CommandHandler("get_news", get_news_cmd))
    app.run_polling()

if __name__ == "__main__":
    main()
