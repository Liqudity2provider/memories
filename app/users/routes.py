from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, abort
from sqlalchemy.orm import sessionmaker
from app.main.utils import iter_pages_, total_users, days_to_summer, total_posts
from app.tables import User, Post
from app import bcrypt, db, Base, mail
from app import engine
from flask_login import login_user, current_user, logout_user, login_required
from app.users.forms import RegForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from app.users.utils import save_picture_thumb, send_reset_email

users = Blueprint('users', __name__)
Base.metadata.create_all(engine)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            session.add(new_user)
            session.commit()
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('users.login'))
        except:
            flash(f'This email is using, try another, please', 'danger')
            return redirect(url_for('users.register'))

    return render_template('register.html', title='Register', form=form, total_users=total_users(),
                           total_posts=total_posts(), days_to_summer=days_to_summer())


@users.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        Session = sessionmaker(bind=engine)
        session = Session()
        user = session.query(User).filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))

        flash('Please check email and password!', 'danger')

    return render_template('login.html', title='Login', form=form, total_users=total_users(),
                           total_posts=total_posts(), days_to_summer=days_to_summer())


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))


@users.route('/account', methods=['POST', 'GET'])
@login_required
def account():
    Session = sessionmaker(bind=engine)
    session = Session()
    current_user_db = session.query(User).get(current_user.id)
    form = UpdateAccountForm()
    if form.picture.data:
        picture_file = save_picture_thumb(form.picture.data)
        current_user_db.image_file = picture_file
        session.commit()
    if form.validate_on_submit():
        current_user_db.username = form.username.data
        current_user_db.email = form.email.data
        session.commit()
    form.username.data = current_user_db.username
    form.email.data = current_user_db.email
    current_user.username = form.username.data
    current_user.email = form.email.data
    image_url = current_user_db.image_file
    return render_template('account.html', title='Account', image_url=image_url, form=form, total_users=total_users(),
                           total_posts=total_posts(), days_to_summer=days_to_summer())


@users.route('/user/<string:username>')
def user_posts(username):
    page = request.args.get('page', default=1, type=int)
    Session = sessionmaker(bind=engine)
    session = Session()
    user = session.query(User).filter_by(username=username).first()
    per_page = 5

    posts = session.query(Post).filter_by(user_id=user.id)
    len_posts = len(list(posts))
    iter_pages = iter_pages_(page, len_posts, per_page)
    posts = session.query(Post).filter_by(user_id=user.id).order_by(Post.date_posted.desc()).slice(
        0 + per_page * (page - 1), per_page + per_page * (page - 1))
    return render_template('user_posts.html', posts=posts, user=user, iter_pages=iter_pages, len_posts=len_posts,
                           total_users=total_users(),
                           total_posts=total_posts(), days_to_summer=days_to_summer())


@users.route('/reset_password', methods=["GET", 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        Session = sessionmaker(bind=engine)
        session = Session()
        user = session.query(User).filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email was sent with the instructions to reset your password', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form, total_users=total_users(),
                           total_posts=total_posts(), days_to_summer=days_to_summer())


@users.route('/reset_password/<token>', methods=["GET", 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        Session = sessionmaker(bind=engine)
        session = Session()
        user_db = session.query(User).get(user.id)
        user_db.password = hashed_password
        session.commit()
        flash(f'Password was changed!', 'success')
        return redirect(url_for('users.login'))

    return render_template('reset_token.html', title='Reset Password', form=form, total_users=total_users(),
                           total_posts=total_posts(), days_to_summer=days_to_summer())
