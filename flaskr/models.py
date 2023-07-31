from flaskr import db, login_manager
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from sqlalchemy.orm import aliased #参照先の複数テーブルを紐づけたい時に使う
from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
from contextlib import contextmanager

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

class User(UserMixin, db.Model):

    __tablename__ = 'users'

