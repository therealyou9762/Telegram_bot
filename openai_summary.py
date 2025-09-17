import os
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Update
from database import add_keyword, get_keywords, add_category, get_categories, add_news, get_news
from newsapi import search_news

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
    try:
        # допустим, обработка ключевых слов:
        kw_list = context.args if context.args else ["Россия"]
        news_list = search_news(kw_list)

        for news in news_list:
            add_news(
                news['title'],
                news['url'],
                news.get('description', ''),  # исправлено с 'summary' на 'description'
                news.get('category', 'Без категории'),
                news['published_at']
            )
            # Отправляем сообщение пользователю (пример)
            message = (
                f"<b>{news['title']}</b>\n"
                f"{news.get('description', '')}\n"
                f"<a href=\"{news['url']}\">Читать подробнее</a>\n"
                f"Категория: {news.get('category', 'Без категории')}\n"
                f"Дата: {news['published_at']}\n"
            )
            await update.message.reply_text(message, parse_mode='HTML')

    except Exception as e:
        logging.exception("Ошибка в get_news_cmd")
        await update.message.reply_text(f"Ошибка при получении новостей: {e}")
        await update.message.reply_html(msg)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("add_keyword", add_keyword_cmd))
    app.add_handler(CommandHandler("list_keywords", list_keywords_cmd))
    app.add_handler(CommandHandler("add_category", add_category_cmd))
    app.add_handler(CommandHandler("list_categories", list_categories_cmd))
    app.add_handler(CommandHandler("get_news", get_news_cmd))
    app.add_handler(CommandHandler("site", site_cmd))
    app.run_polling()

async def site_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    url = f"https://telegr77-6209977497ad.herokuapp.com/?user_id={user_id}"  # твой реальный домен!
    await update.message.reply_text(
        f"Перейдите на сайт управления новостями: {url}"
    )

if __name__ == "__main__":
    main()
