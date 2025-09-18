from flask import Flask
from db.models import db
from flask_migrate import Migrate

from web.app import app as flask_app
from bot.bot import main as bot_main
import threading
import os

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL

db.init_app(flask_app)
migrate = Migrate(flask_app, db)

def start_web():
    flask_app.run(host="0.0.0.0", port=5000)

def start_bot():
    bot_main()

if __name__ == "__main__":
    threading.Thread(target=start_web).start()
    threading.Thread(target=start_bot).start()
