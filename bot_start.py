from telegram.ext import Application, CommandHandler

async def start(update, context):
    await update.message.reply_text('Бот работает!')

app = Application.builder().token("ВАШ_ТОКЕН").build()
app.add_handler(CommandHandler("start", start))

if __name__ == '__main__':
    app.run_polling()
