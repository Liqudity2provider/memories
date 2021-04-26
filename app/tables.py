from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from app import db, login_manager, ma
from flask_login import UserMixin


class PostModel(db.Model):
    __tablename__ = 'post'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(100), nullable=False,
                           default='https://firebasestorage.googleapis.com/v0/b/memories-9ec47.appspot.com/o/default.jpg?alt=media&token=7918cd36-d3f9-4b0b-868e-2207e6761eac')

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"


class PostSchema(ma.SQLAlchemyAutoSchema):
    """Generate marshmallow schema for Post model"""

    class Meta:
        model = PostModel
        include_fk = True


@login_manager.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))


class UserModel(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False,
                           default='https://firebasestorage.googleapis.com/v0/b/memories-9ec47.appspot.com/o/default'
                                   '.jpg?alt=media&token=7918cd36-d3f9-4b0b-868e-2207e6761eac')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('PostModel', backref='author', lazy='dynamic')

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
        return UserModel.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class UserSchema(ma.SQLAlchemyAutoSchema):
    """Generate marshmallow schema for User model"""

    class Meta:
        model = UserModel

    id = ma.auto_field()
    username = ma.auto_field()
    posts = ma.auto_field()


