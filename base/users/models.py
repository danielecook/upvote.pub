# -*- coding: utf-8 -*-
"""
"""
from base.utils.misc import now
from base import db
from base.users import constants as USER
from base.threads.models import thread_upvotes, comment_upvotes
from base.utils.misc import random_string
from base.subreddits.constants import BASE_SUBREDDITS

class User(db.Model):
    """
    """
    __tablename__ = 'users_user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(USER.MAX_USERNAME), unique=True)
    email = db.Column(db.String(USER.MAX_EMAIL), unique=True)
    email_verified = db.Column(db.Boolean())
    email_token = db.Column(db.String(18), default=random_string)
    password = db.Column(db.String(USER.MAX_PASSW))
    created_on = db.Column(db.DateTime, default=now)

    threads = db.relationship('Thread', backref='user', lazy='dynamic')
    comments = db.relationship('Comment', backref='user', lazy='dynamic')
    subreddits = db.relationship('Subreddit', backref='user', lazy='dynamic')

    university = db.Column(db.String(100))

    status = db.Column(db.SmallInteger, default=USER.ALIVE)
    role = db.Column(db.SmallInteger, default=USER.USER)

    subreddit_subs = db.Column(db.JSON, default={"subs": sum(BASE_SUBREDDITS.values(), [])})

    def __repr__(self):
        return '<User %r>' % (self.username)

    def get_status(self):
        """
        returns string form of status, 0 = 'dead', 1 = 'alive'
        """
        return USER.STATUS[self.status]

    def get_role(self):
        """
        analogous to above but for roles
        """
        return USER.ROLE[self.role]


    def get_thread_karma(self):
        """
        fetch the number of votes this user has had on his/her threads

        1.) Get id's of all threads by this user

        2.) See how many of those threads also were upvoted but not by
        the person him/her self.
        """
        thread_ids = [t.id for t in self.threads]
        select = thread_upvotes.select(db.and_(
                thread_upvotes.c.thread_id.in_(thread_ids),
                thread_upvotes.c.user_id != self.id
            )
        )
        rs = db.engine.execute(select)
        return rs.rowcount

    def get_comment_karma(self):
        """
        fetch the number of votes this user has had on his/her comments
        """
        comment_ids = [c.id for c in self.comments]
        select = comment_upvotes.select(db.and_(
                comment_upvotes.c.comment_id.in_(comment_ids),
                comment_upvotes.c.user_id != self.id
            )
        )
        rs = db.engine.execute(select)
        return rs.rowcount

