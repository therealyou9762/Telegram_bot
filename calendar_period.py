from telegram_bot_calendar import DetailedTelegramCalendar
import datetime

# ... (твой существующий импорт и setup)

CALENDAR_START, CALENDAR_END, KEYWORDS = range(3)

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
        await update.callback_query.edit_message_text(f"Выберите начальную дату:", reply_markup=key)
        return CALENDAR_START
    elif result:
        context.user_data['start_date'] = result
        calendar, step = DetailedTelegramCalendar().build()
        await update.callback_query.edit_message_text("Выберите конечную дату:", reply_markup=calendar)
        return CALENDAR_END

async def calendar_end(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result, key, step = DetailedTelegramCalendar().process(update.callback_query.data)
    if not result and key:
        await update.callback_query.edit_message_text(f"Выберите конечную дату:", reply_markup=key)
        return CALENDAR_END
    elif result:
        context.user_data['end_date'] = result
        await update.callback_query.edit_message_text("Введите ключевые слова для поиска (через запятую):")
        return KEYWORDS

async def keywords_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    keywords = [kw.strip() for kw in text.split(',') if kw.strip()]
    context.user_data['keywords'] = keywords

    start_date = context.user_data.get('start_date')
    end_date = context.user_data.get('end_date')
    news_items = filter_news(start_date, end_date, keywords)

    if not news_items:
        await update.message.reply_text("📰 Новости не найдены по этим параметрам.")
        return ConversationHandler.END

    for item in news_items[:10]:
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
        PERIOD: [
            CallbackQueryHandler(period_chosen),
        ],
        CALENDAR_START: [
            CallbackQueryHandler(calendar_start, per_message=True)
        ],
        CALENDAR_END: [
            CallbackQueryHandler(calendar_end, per_message=True)
        ],
        KEYWORDS: [
            MessageHandler(filters.TEXT & (~filters.COMMAND), keywords_chosen)
        ],
    },
    fallbacks=[],
)
