# -*- coding: utf-8 -*-
"""
All view code for async get/post calls towards the server
must be contained in this file.
"""
import arrow
from flask import (Blueprint, request, render_template, flash, g,
        session, redirect, url_for, jsonify, abort)
from werkzeug import check_password_hash, generate_password_hash
from logzero import logger
from base import db
from base.users.models import User
from base.threads.models import Thread, Comment
from base.users.decorators import requires_login
from base.utils.misc import generate_csrf_token
from base.utils.text_utils import format_comment

mod = Blueprint('apis', __name__, url_prefix='/apis')


@mod.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@mod.before_request
def csrf_protect():
    if request.method == "POST":
        token = session.pop('csrf_token', None)
        if not token or token != request.form.get('csrf_token'):
            abort(403)


@mod.route('/comments/submit/', methods=['POST'])
@requires_login
def submit_comment():
    """
    Submit comments via ajax
    """
    # Check that user has not submitted more than 20 comments
    # in the last hour.

    user_id = g.user.id
    if not user_id:
        abort(404)
    since = arrow.utcnow() - arrow.utcnow().shift(hours=-1).datetime
    submission_count = Comment.query.filter(Comment.user_id == user_id, Comment.created_on > since).count()
    if submission_count >= 20:
        return jsonify(error='You have been submitting too many comments')

    thread_id = int(request.form['thread_id'])
    comment_text = request.form['comment_text']
    comment_parent_id = request.form['parent_id']  # empty means none

    if not comment_text:
        abort(404)

    thread = Thread.query.get_or_404(int(thread_id))
    thread.n_comments += 1
    db.session.commit()
    comment = thread.add_comment(comment_text,
                                 comment_parent_id,
                                 g.user.id)


    return jsonify(comment_text=format_comment(comment.text),
                   date=comment.pretty_date(),
                   username=g.user.username,
                   comment_id=comment.id,
                   csrf_token=generate_csrf_token())


@mod.route('/threads/vote/', methods=['POST'])
@requires_login
def vote_thread():
    """
    Submit votes via ajax
    """
    thread_id = int(request.form['thread_id'])
    user_id = g.user.id

    if not thread_id:
        abort(404)

    thread = Thread.query.get_or_404(int(thread_id))
    vote_status = thread.vote(user_id=user_id)
    return jsonify(new_votes=thread.votes,
                   vote_status=vote_status,
                   csrf_token=generate_csrf_token())


@mod.route('/threads/save/', methods=['POST'])
@requires_login
def save_thread():
    """
    Submit votes via ajax
    """
    thread_id = int(request.form['thread_id'])
    user_id = g.user.id

    if not thread_id:
        abort(404)

    thread = Thread.query.get_or_404(int(thread_id))
    save_status = thread.save(user_id=user_id)
    return jsonify(new_saves=thread.saves,
                   save_status=save_status,
                   csrf_token=generate_csrf_token())


@mod.route('/comments/vote/', methods=['POST'])
@requires_login
def vote_comment():
    """
    Submit votes via ajax
    """
    comment_id = int(request.form['comment_id'])
    user_id = g.user.id

    if not comment_id:
        abort(404)

    comment = Comment.query.get_or_404(int(comment_id))
    comment.vote(user_id=user_id)
    logger.info(comment.votes)
    return jsonify(votes=comment.votes,
                   csrf_token=generate_csrf_token())

