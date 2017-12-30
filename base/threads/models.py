# -*- coding: utf-8 -*-
"""
All database abstractions for threads and comments
go in this file.

CREATE TABLE `thread_upvotes` (
  `user_id` int(11) DEFAULT NULL,
  `thread_id` int(11) DEFAULT NULL,
  KEY `user_id` (`user_id`),
  KEY `thread_id` (`thread_id`),
  CONSTRAINT `thread_upvotes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`),
  CONSTRAINT `thread_upvotes_ibfk_2` FOREIGN KEY (`thread_id`) REFERENCES `threads_thread` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1

CREATE TABLE `comment_upvotes` (
  `user_id` int(11) DEFAULT NULL,
  `comment_id` int(11) DEFAULT NULL,
  KEY `user_id` (`user_id`),
  KEY `comment_id` (`comment_id`),
  CONSTRAINT `comment_upvotes_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users_user` (`id`),
  CONSTRAINT `comment_upvotes_ibfk_2` FOREIGN KEY (`comment_id`) REFERENCES `threads_comment` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 |
"""
from base import db
from base.threads import constants as THREAD
from base import utils
from base import media
from math import log
import datetime
import arrow
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy import text

thread_upvotes = db.Table('thread_upvotes',
    db.Column('user_id', db.Integer, db.ForeignKey('users_user.id')),
    db.Column('thread_id', db.Integer, db.ForeignKey('threads_thread.id'))
)

comment_upvotes = db.Table('comment_upvotes',
    db.Column('user_id', db.Integer, db.ForeignKey('users_user.id')),
    db.Column('comment_id', db.Integer, db.ForeignKey('threads_comment.id'))
)

class Thread(db.Model):
    """
    We will mimic reddit, with votable threads. Each thread may have either
    a body text or a link, but not both.
    """
    __tablename__ = 'threads_thread'
    id = db.Column(db.Integer, primary_key=True)

    # Publication information
    pub_title = db.Column(db.String(300))
    pub_authors = db.Column(db.String(1000))
    pub_abstract = db.Column(db.Text())
    pub_doi = db.Column(db.String(250))
    pub_pmid = db.Column(db.Integer())
    pub_pmc = db.Column(db.Integer())
    pub_arxiv = db.Column(db.String(25))
    pub_biorxiv = db.Column(db.String(250))
    pub_biorxiv_url = db.Column(db.String(250))
    pub_url = db.Column(db.String(250))
    pub_pdf_url = db.Column(db.String(250))
    pub_journal = db.Column(db.String(100))
    pub_date = db.Column(db.DateTime)

    text_comment = db.Column(db.String(3000), default=None)

    thumbnail = db.Column(db.String(THREAD.MAX_LINK), default=None)

    user_id = db.Column(db.Integer, db.ForeignKey('users_user.id'))
    subreddit_id = db.Column(db.Integer, db.ForeignKey('subreddits_subreddit.id'))

    created_on = db.Column(db.DateTime, default=arrow.utcnow().datetime)
    updated_on = db.Column(db.DateTime, default=arrow.utcnow().datetime, onupdate=arrow.utcnow().datetime)
    comments = db.relationship('Comment', backref='thread', lazy='dynamic')

    status = db.Column(db.SmallInteger, default=THREAD.ALIVE)

    votes = db.Column(db.Integer, default=1)
    hotness = db.column_property(db.func.ROUND(100+(db.func.LN(votes)*50 - db.func.POW(db.func.LN(db.func.TIMESTAMPDIFF(text('SECOND'), created_on, db.func.UTC_TIMESTAMP())), 2)), 2))


    def __repr__(self):
        return '<Thread %r>' % (self.pub_title)

    def get_comments(self, order_by='timestamp'):
        """
        default order by timestamp
        return top level
        """
        if order_by == 'timestamp':
            return self.comments.filter_by(depth=1).\
                order_by(db.desc(Comment.created_on)).all()[:THREAD.MAX_COMMENTS]
        else:
            return self.comments.filter_by(depth=1).\
                order_by(db.desc(Comment.created_on)).all()[:THREAD.MAX_COMMENTS]

    def get_status(self):
        """
        returns string form of status, 0 = 'dead', 1 = 'alive'
        """
        return THREAD.STATUS[self.status]


    def pretty_date(self, typeof='created'):
        """
        returns a humanized version of the raw age of this thread,
        eg: 34 minutes ago versus 2040 seconds ago.
        """

        return arrow.get(self.created_on).humanize()

    def add_comment(self, comment_text, comment_parent_id, user_id):
        """
        add a comment to this particular thread
        """
        if len(comment_parent_id) > 0:
            # parent_comment = Comment.query.get_or_404(comment_parent_id)
            # if parent_comment.depth + 1 > THREAD.MAX_COMMENT_DEPTH:
            #    flash('You have exceeded the maximum comment depth')
            comment_parent_id = int(comment_parent_id)
            comment = Comment(thread_id=self.id, user_id=user_id,
                    text=comment_text, parent_id=comment_parent_id)
        else:
            comment = Comment(thread_id=self.id, user_id=user_id,
                    text=comment_text)

        db.session.add(comment)
        db.session.commit()
        comment.set_depth()
        return comment

    def get_voter_ids(self):
        """
        return ids of users who voted this thread up
        """
        select = thread_upvotes.select(thread_upvotes.c.thread_id==self.id)
        rs = db.engine.execute(select)
        ids = rs.fetchall() # list of tuples
        return ids

    def has_voted(self, user_id):
        """
        did the user vote already
        """
        select_votes = thread_upvotes.select(
                db.and_(
                    thread_upvotes.c.user_id == user_id,
                    thread_upvotes.c.thread_id == self.id
                )
        )
        rs = db.engine.execute(select_votes)
        return False if rs.rowcount == 0 else True

    def vote(self, user_id):
        """
        allow a user to vote on a thread. if we have voted already
        (and they are clicking again), this means that they are trying
        to unvote the thread, return status of the vote for that user
        """
        already_voted = self.has_voted(user_id)
        vote_status = None
        if not already_voted:
            # vote up the thread
            db.engine.execute(
                thread_upvotes.insert(),
                user_id = user_id,
                thread_id = self.id
            )
            self.votes = self.votes + 1
            vote_status = True
        else:
            # unvote the thread
            db.engine.execute(
                thread_upvotes.delete(
                    db.and_(
                        thread_upvotes.c.user_id == user_id,
                        thread_upvotes.c.thread_id == self.id
                    )
                )
            )
            self.votes = self.votes - 1
            vote_status = False
        db.session.commit() # for the vote count
        return vote_status


class Comment(db.Model):
    """
    This class is here because comments can only be made on threads,
    so it is contained completly in the threads module.

    Note the parent_id and children values. A comment can be commented
    on, so a comment has a one to many relationship with itself.

    Backrefs:
        A comment can refer to its parent thread with 'thread'
        A comment can refer to its parent comment (if exists) with 'parent'
    """
    __tablename__ = 'threads_comment'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(THREAD.MAX_BODY), default=None)

    user_id = db.Column(db.Integer, db.ForeignKey('users_user.id'))
    thread_id = db.Column(db.Integer, db.ForeignKey('threads_thread.id'))

    parent_id = db.Column(db.Integer, db.ForeignKey('threads_comment.id'))
    children = db.relationship('Comment', backref=db.backref('parent',
            remote_side=[id]), lazy='dynamic')

    depth = db.Column(db.Integer, default=1) # start at depth 1

    created_on = db.Column(db.DateTime, default=arrow.utcnow().datetime)
    updated_on = db.Column(db.DateTime, default=arrow.utcnow().datetime, onupdate=arrow.utcnow().datetime)

    votes = db.Column(db.Integer, default=1)

    def __repr__(self):
        return '<Comment %r>' % (self.text[:25])

    def __init__(self, thread_id, user_id, text, parent_id=None):
        self.thread_id = thread_id
        self.user_id = user_id
        self.text = text
        self.parent_id = parent_id

    def set_depth(self):
        """
        call after initializing
        """
        if self.parent:
            self.depth = self.parent.depth + 1
            db.session.commit()

    def get_comments(self, order_by='timestamp'):
        """
        default order by timestamp
        """
        if order_by == 'timestamp':
            return self.children.order_by(db.desc(Comment.created_on)).\
                all()[:THREAD.MAX_COMMENTS]
        else:
            return self.comments.order_by(db.desc(Comment.created_on)).\
                all()[:THREAD.MAX_COMMENTS]

    def get_margin_left(self):
        """
        nested comments are pushed right on a page
        -15px is our default margin for top level comments
        """
        margin_left = 15 + ((self.depth-1) * 32)
        margin_left = min(margin_left, 680)
        return str(margin_left) + "px"


    def pretty_date(self, typeof='created'):
        """
        returns a humanized version of the raw age of this thread,
        eg: 34 minutes ago versus 2040 seconds ago.
        """
        if typeof == 'created':
            return arrow.get(self.created_on).humanize()
        elif typeof == 'updated':
            return arrow.get(self.updated_on).humanize()


    def vote(self, direction):
        """
        """
        pass

    def comment_on(self):
        """
        when someone comments on this particular comment
        """
        pass
