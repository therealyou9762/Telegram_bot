import threading
from web.app import app as flask_app
from bot.bot import main as bot_main

def start_web():
    flask_app.run(host="0.0.0.0", port=5000)

def start_bot():
    bot_main()

if __name__ == "__main__":
    threading.Thread(target=start_web).start()
    threading.Thread(target=start_bot).start()
