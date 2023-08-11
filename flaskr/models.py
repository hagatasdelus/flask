from flaskr import db, login_manager
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
# from sqlalchemy.orm import aliased
# from sqlalchemy import and_, or_, desc
from datetime import datetime, timedelta
from contextlib import contextmanager
from uuid import uuid4

@contextmanager
def transaction():
    try:
        yield
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class BookInfo(db.Model):

    __tablename__ = 'book_infos'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64), index=True, nullable=False)
    genre = db.Column(db.String(64), index=True, unique=False)
    price = db.Column(db.Integer, nullable=False)
    arrival_day = db.Column(db.DateTime, default=datetime.now)
    picture_path = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def __init__(self, title, price, genre, arrival_day, user_id):
        self.title = title
        self.price = price
        self.genre = genre
        self.arrival_day = arrival_day
        self.user_id = user_id

    def create_new_book(self):
        db.session.add(self)
    
    # @classmethod
    # def select_book_by_title(cls, title, page=1):
    #     return cls.query.filter(
    #         cls.title.like(f'%{title}%')
    #     ).order_by(cls.title).paginate(page=page, per_page=50, error_out=False)
    
    # @classmethod
    # def select_book_by_genre(cls, genre, page=1):
    #     return cls.query.filter(
    #         cls.genre.like(f'%{genre}%')
    #     ).order_by(cls.genre).paginate(page=page, per_page=50, error_out=False)

    @classmethod
    def get_books(cls):
        return cls.query.order_by(
            cls.arrival_day.desc()
        ).limit(10).all()
    
    @classmethod
    def get_book_by_id(cls, id):
        return cls.query.get(id)
    
    @classmethod
    def delete_book(cls, id):    
        cls.query.filter_by(id=int(id)).delete()
      
class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128), default = generate_password_hash('libraryapp'))
    is_active = db.Column(db.Boolean, unique=False, default=False)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, username, email):
        self.username = username
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
    
    def save_new_password(self, new_password):
        self.password = generate_password_hash(new_password)
        self.is_active = True

class PasswordResetToken(db.Model):

    __tablename__ = 'password_reset_tokens'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(
        db.String(64),
        unique=True,
        index=True,
        server_default = str(uuid4)
    )
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    expire_at = db.Column(db.DateTime, default=datetime.now)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, token, user_id, expire_at):
        self.token = token
        self.user_id = user_id
        self.expire_at = expire_at

    """パスワード設定用のURLを生成"""
    @classmethod
    def publish_token(cls, user):
        token = str(uuid4())
        new_token = cls(
            token,
            user.id,
            datetime.now() + timedelta(days=1)
        )
        db.session.add(new_token)
        return token
    
    @classmethod
    def get_user_id_by_token(cls, token):
        now = datetime.now()
        record = cls.query.filter_by(token=str(token)).filter(cls.expire_at > now).first()  #expire_atが現在時刻よりもすぎていない.
        if record:
            return record.user_id
        else:
            return None
        
    @classmethod
    def delete_token(cls, token):    
        cls.query.filter_by(token=str(token)).delete()
