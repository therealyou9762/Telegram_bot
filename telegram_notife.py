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
