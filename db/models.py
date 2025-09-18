from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.BigInteger, primary_key=True)  # Telegram ID
    name = db.Column(db.String(128))
    username = db.Column(db.String(128))

    def __init__(self, id, name, username):
        self.id = id
        self.name = name
        self.username = username
