import math

from sqlalchemy.orm import sessionmaker

from app import db
from app.tables import UserModel
from app.tables import PostModel


def iter_pages_(page_now, len_posts, post_per_page):
    res_list = []
    max_page = math.ceil(len_posts / post_per_page)
    if max_page < 11:
        res_list = [i for i in range(1, max_page + 1)]
    else:
        if page_now <= 5:
            res_list = [1, 2, 3, 4, 5, 6, 7, None, max_page - 1, max_page]
        elif 5 < page_now < max_page - 2:
            res_list = [1, None, page_now - 2, page_now - 1, page_now, page_now + 1, page_now + 2, None, max_page]
        elif page_now >= max_page - 2:
            res_list = [1, 2, None, max_page - 4, max_page - 3, max_page - 2, max_page - 1, max_page]
    return res_list


def total_users():
    return UserModel.query.count()


def total_posts():
    return PostModel.query.count()


def days_to_summer():
    import datetime
    today = datetime.date.today()
    someday = datetime.date(2021, 6, 1)
    diff = someday - today
    return diff.days


