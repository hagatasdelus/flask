from flaskr import db, login_manager
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
# from sqlalchemy.orm import aliased
# from sqlalchemy import and_, or_, desc
from datetime import datetime#, timedelta
from contextlib import contextmanager
from random import randint

@contextmanager
def transaction():
    try:
        yield
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

class BookInfo:
    def __init__(self, number, title, genre, price, arrival_day, picture_path):
        self.number = number
        self.title = title
        self.genre = genre
        self.price = price
        self.arrival_day = arrival_day
        self.picture_path = picture_path

@login_manager.user_loader #htmlのcurrent_user.is_authenticatedでユーザ情報を取りに来る。ユーザが既に認証されたのかを確認できる
def load_user(user_id):
    return User.query.get(user_id)

class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, default=lambda: str(randint(10**7, 10**8-1)))
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128), default = generate_password_hash('libraryapp'))
    is_active = db.Column(db.Boolean, unique=False, default=False)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, email):
        self.email = email

    def validate_password(self, password):
        return check_password_hash(self.password, password)
    
    def create_new_user(self):
        db.session.add(self)

    @classmethod
    def select_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()
    @classmethod
    def select_user_by_id(cls, id):
        return cls.query.get(id)
    