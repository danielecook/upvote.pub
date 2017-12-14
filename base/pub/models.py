# -*- coding: utf-8 -*-
"""

Publication ID Database

"""
from base import db
from base.pub import constants as PUB
from base.threads.models import Thread
from base import utils
import datetime

class pub_id_db(db.Model):
    """
    """
    __tablename__ = 'subreddits_subreddit'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(SUBREDDIT.MAX_NAME), unique=True)
    desc = db.Column(db.String(SUBREDDIT.MAX_DESCRIPTION))

    admin_id = db.Column(db.Integer, db.ForeignKey('users_user.id'))

    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    threads = db.relationship('Thread', backref='subreddit', lazy='dynamic')
    status = db.Column(db.SmallInteger, default=SUBREDDIT.ALIVE)


