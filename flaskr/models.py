from flaskr import db, login_manager
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin, current_user
from sqlalchemy.orm import relationship
from sqlalchemy import desc, and_
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
    arrival_day = db.Column(db.Date, default=datetime.now().date)
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

    @classmethod
    def get_books(cls):
        return cls.query.order_by(
            cls.arrival_day.desc()
        ).all()
    
    @classmethod
    def select_book_by_id(cls, id):
        return cls.query.get(id)
    
    @classmethod
    def delete_book(cls, id):    
        cls.query.filter_by(id=int(id)).delete()

    @classmethod
    def select_book_by_title(cls, title):
        return cls.query.filter_by(title=title).first()
      
class User(UserMixin, db.Model):

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(128), default = generate_password_hash('libraryapp'))
    is_active = db.Column(db.Boolean, unique=False, default=False)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    boards = relationship("Board", back_populates="user")

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

class Board(db.Model):

    __tablename__ = 'boards'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book_infos.id'), index=True)
    from_user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    post = db.Column(db.Text)
    read = db.Column(db.Boolean, default=False)
    create_at = db.Column(db.DateTime, default=datetime.now)
    update_at = db.Column(db.DateTime, default=datetime.now)

    user = relationship("User", back_populates="boards")

    def __init__(self, from_user_id, book_id, post):
        self.from_user_id = from_user_id
        self.book_id = book_id
        self.post = post

    def create_post(self):
        db.session.add(self)

    @classmethod
    def get_book_posts(cls, book_id, offset_value=0, limit_value=100):
        return cls.query.filter_by(
            book_id=book_id
        ).order_by(
            desc(cls.id)
        ).offset(offset_value).limit(limit_value).all()
    
    @classmethod
    def delete_posts_by_book_id(cls, book_id):
        return cls.query.filter_by(
                book_id=book_id
            ).delete()
    
    @classmethod
    def update_read_by_ids(cls, ids):
        cls.query.filter(cls.id.in_(ids)).update(
            {'read': True},
            synchronize_session='fetch'
        )

    @classmethod
    def select_not_read_posts(cls, book_id):
        return cls.query.filter(
            and_(
                cls.from_user_id != int(current_user.get_id()),
                cls.book_id == book_id,
                cls.read == 0
            )
        ).order_by(cls.id).all()
