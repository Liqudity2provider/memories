from flask_wtf import FlaskForm
from sqlalchemy.orm import sessionmaker
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed
from app import db
from app.tables import UserModel


class RegForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign in')

    def validate_username(self, username):
        exists = db.session.query(UserModel).filter_by(username=username.data).first()
        if exists:
            raise ValidationError('This name is taken. Please choose another')

    def validate_email(self, email):
        exists = db.session.query(UserModel).filter_by(email=email.data).first()
        if exists:
            raise ValidationError('This email is taken. Please choose another')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):
    """
    form that updating user information at account page
    """
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_username(self, username):

        if username.data != current_user.username:
            exists = db.session.query(UserModel).filter_by(username=username.data).first()
            if exists:
                raise ValidationError('This name is taken. Please choose another')

    def validate_email(self, email):
        if email.data != current_user.email:
            exists = db.session.query(UserModel).filter_by(email=email.data).first()
            if exists:
                raise ValidationError('This email is taken. Please choose another')


class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset password')

    def validate_email(self, email):
        exists = db.session.query(UserModel).filter_by(email=email.data).first()
        if exists is None:
            raise ValidationError('There is no account with that email. Please register first.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
