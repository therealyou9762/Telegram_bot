import telebot
from models import User, db

TOKEN = 'ВАШ_ТОКЕН_ТЕЛЕГРАМ'
bot = telebot.TeleBot(TOKEN)

# Пример настройки SQLAlchemy (Flask не обязателен, но часто используется)
from flask import Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://<user>:<password>@<host>:<port>/<dbname>'
db.init_app(app)

with app.app_context():
    db.create_all()  # создаёт таблицы, если их нет

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    username = message.from_user.username

    with app.app_context():
        user = User.query.filter_by(id=user_id).first()
        if not user:
            user = User(id=user_id, name=name, username=username)
            db.session.add(user)
            try:
                db.session.commit()
                bot.send_message(message.chat.id, "Вы зарегистрированы!")
            except Exception as e:
                db.session.rollback()
                bot.send_message(message.chat.id, f"Ошибка при регистрации: {e}")
        else:
            bot.send_message(message.chat.id, "Вы уже зарегистрированы.")

bot.polling(none_stop=True)
