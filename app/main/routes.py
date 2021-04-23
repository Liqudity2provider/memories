from flask import Blueprint, request
from flask import render_template, url_for, flash, redirect, request, abort
from sqlalchemy.orm import sessionmaker
from app.main.utils import iter_pages_, total_users, total_posts, days_to_summer
from app.tables import User, Post
from app import engine

main = Blueprint('main', __name__)


@main.route('/')
@main.route('/home')
def home():
    page = request.args.get('page', default=1, type=int)
    Session = sessionmaker(bind=engine)
    session = Session()

    per_page = 5
    posts = session.query(Post)
    iter_pages = iter_pages_(page, len(list(posts)), per_page)
    posts = session.query(Post).order_by(Post.date_posted.desc()).slice(0 + per_page * (page - 1),
                                                                        per_page + per_page * (page - 1))

    return render_template('home.html', posts=posts, page=page, iter_pages=iter_pages, total_users=total_users(),
                           total_posts=total_posts(), days_to_summer=days_to_summer())


@main.route('/about')
def about():
    return render_template('about.html', title='About', total_users=total_users(),
                           total_posts=total_posts(), days_to_summer=days_to_summer())
