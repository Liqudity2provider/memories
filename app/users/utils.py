import os
from email.mime.text import MIMEText

from PIL import Image
from flask import url_for
import secrets
from app import mail, Config
from flask import current_app
from flask_mail import Message
import pyrebase
import smtplib


def save_picture_thumb(form_picture):
    reandom_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    filename_hexed = reandom_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/photos', filename_hexed)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    url_image = put_image(os.path.join(current_app.root_path, 'static/photos/'), filename_hexed, filename_hexed)
    # Clean-up temp image
    os.remove(picture_path)

    return url_image


def save_picture(form_picture):
    reandom_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    filename_hexed = reandom_hex + f_ext
    picture_path = os.path.join(current_app.root_path, 'static/photos', filename_hexed)
    output_size = (540, 540)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(picture_path)

    url_image = put_image(os.path.join(current_app.root_path, 'static/photos/'), filename_hexed, filename_hexed)
    # Clean-up temp image
    os.remove(picture_path)

    return url_image


def send_reset_email(user):

    smtpObj = smtplib.SMTP('smtp.googlemail.com', 587)
    smtpObj.starttls()
    smtpObj.login('commerce.tf@gmail.com', 'alex2811')

    token = user.get_reset_token()

    msg = '\n' + f'{url_for("users.reset_token", token=token, _external=True)}'
    smtpObj.sendmail(from_addr="commerce.tf@gmail.com", to_addrs=user.email, msg=msg)


def put_image(path_to_file, filename, new_filename):
    firebase_storage = pyrebase.initialize_app(config=Config.FIREBASE_CONFIG)
    storage = firebase_storage.storage()
    storage.child(new_filename).put(path_to_file + filename)
    return get_url_of_image(new_filename)


def get_url_of_image(firebase_file_name):
    firebase_storage = pyrebase.initialize_app(Config.FIREBASE_CONFIG)
    storage = firebase_storage.storage()

    email = 'commerce.tf@gmail.com'
    password = 'alex2811'
    auth = firebase_storage.auth()

    user = auth.sign_in_with_email_and_password(email, password)
    url = storage.child(firebase_file_name).get_url(user['idToken'])
    import re
    url = re.findall('(.+)&token', url)[0]
    return url


def delete_obj():
    pass
