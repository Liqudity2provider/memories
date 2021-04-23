from datetime import datetime

from sqlalchemy.orm import sessionmaker
from flask_login import UserMixin
from app import Base, db, engine, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app


@login_manager.user_loader
def load_user(user_id):
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).get(user_id)
    return user


class User(Base, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='https://firebasestorage.googleapis.com/v0/b/memories-9ec47.appspot.com/o/default'
                                   '.jpg?alt=media&token=7918cd36-d3f9-4b0b-868e-2207e6761eac')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        Session = sessionmaker(bind=engine)
        session = Session()
        return session.query(User).get(user_id)

    def __repr__(self):
        return f'User("{self.id}", "{self.username}", "{self.email}", "{self.image_file}")'


class Post(Base):
    __tablename__ = 'Post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False, )
    image_file = db.Column(db.String(100), nullable=False,
                           default='https://firebasestorage.googleapis.com/v0/b/memories-9ec47.appspot.com/o/default.jpg?alt=media&token=7918cd36-d3f9-4b0b-868e-2207e6761eac')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'Post("{self.title}", "{self.date_posted}", "{self.image_file}")'
