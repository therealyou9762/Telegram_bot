import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Telegram
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

    # Database
    DATABASE_URL = os.getenv('DATABASE_URL')

    # APIs
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')