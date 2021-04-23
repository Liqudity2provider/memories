from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, abort
from sqlalchemy.orm import sessionmaker

from app.main.utils import total_users, days_to_summer, total_posts
from app.post.forms import PostForm
from app.tables import User, Post
from app import engine
from flask_login import login_user, current_user, logout_user, login_required

from app.users.utils import save_picture

posts = Blueprint('posts', __name__)


@posts.route('/post/new', methods=['POST', 'GET'])
@login_required
def new_post():
    Session = sessionmaker(bind=engine)
    session = Session()
    form = PostForm()
    picture_file = None
    if form.picture.data:
        picture_file = save_picture(form.picture.data)
    if form.validate_on_submit():
        new_post_ = Post(title=form.title.data, content=form.content.data, user_id=current_user.id,
                         image_file=picture_file)
        try:
            session.add(new_post_)
            session.commit()
            flash('Post has been create', 'success')
            return redirect(url_for('main.home'))
        except:
            flash('Adding to db went wrong!', 'danger')

    return render_template('create_post.html', title='New Post', form=form, legend='New Post',
                           total_users=total_users(),
                           total_posts=total_posts(), days_to_summer=days_to_summer())


@posts.route('/post/<int:post_id>', methods=['POST', 'GET'])
def post(post_id):
    Session = sessionmaker(bind=engine)
    session = Session()
    post = session.query(Post).get(post_id)
    return render_template('post.html', title=post.title, post=post, total_users=total_users(),
                           total_posts=total_posts(), days_to_summer=days_to_summer())


@posts.route('/post/<int:post_id>/update', methods=['POST', 'GET'])
@login_required
def update_post(post_id):
    Session = sessionmaker(bind=engine)
    session = Session()
    post = session.query(Post).get(post_id)

    if post.author != current_user:
        abort(403)

    form = PostForm()

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            post.image_file = picture_file
        session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('posts.post', post_id=post_id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content

    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post',
                           total_users=total_users(),
                           total_posts=total_posts(), days_to_summer=days_to_summer())


@posts.route('/post/<int:post_id>/delete', methods=['POST', 'GET'])
@login_required
def delete_post(post_id):
    Session = sessionmaker(bind=engine)
    session = Session()
    post = session.query(Post).get(post_id)
    session.delete(post)
    session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('main.home'))
