# -*- coding: utf-8 -*-
"""
"""
from logzero import logger
from flask import (Blueprint, request, render_template, flash, g, session,
                   redirect, url_for, abort)
from slugify import slugify
from base.threads.forms import submit_pub_form
from base.threads.models import Thread
from base.users.models import User
from base.subreddits.models import Subreddit
from base.frontends.views import get_subreddits
from base import db
from base.utils.pubs import fetch_pub
from base.utils.pub_ids import id_type, get_pub_thread
from base.utils.misc import random_string


mod = Blueprint('threads', __name__, url_prefix='/r')

#################
# Threads Views #
#################


@mod.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])



@mod.route('/<subreddit_name>/submit/', methods=['GET', 'POST'])
def submit(subreddit_name=None):
    """
    """
    if g.user is None:
        flash('You must be logged in to submit posts!', 'danger')
        return redirect(url_for('frontends.login', next=request.path))

    user_id = g.user.id

    subreddit = Subreddit.query.filter_by(name=subreddit_name).first()
    if not subreddit:
        abort(404)

    form = submit_pub_form(request.form)

    # Check if pub has already been submitted
    if form.pub_id.data:
        thread = get_pub_thread(form.pub_id.data)
        logger.debug(form.pub_id.data)
        if thread:
            flash('That pub has already been submitted!', 'warning')
            return redirect(url_for('threads.thread_permalink',
                                    thread_id=thread.id,
                                    subreddit_name=thread.subreddit.name,
                                    title=slugify(thread.pub_title)))

    if form.validate_on_submit():
        # Fetch data from publication
        pub_id = form.pub_id.data
        pub_data = fetch_pub(pub_id)
        text = form.text.data.strip()

        if not pub_data:
            flash("Could not find a pub with the ID: '{}'".format(form.pub_id.data), 'danger')
            return render_template('threads/submit_post.html', form=form, cur_subreddit=subreddit.name)

        thread = Thread(text_comment=text, user_id=user_id, subreddit_id=subreddit.id, **pub_data)

        db.session.add(thread)
        db.session.commit()
        flash("Thank you for submitting!", "success")
        return redirect(url_for('threads.thread_permalink',
                                thread_id=thread.id,
                                subreddit_name=thread.subreddit.name,
                                title = slugify(thread.pub_title)))
    return render_template('threads/submit_post.html',
                           form=form,
                           page_title='Submit to ' + subreddit_name,
                           cur_subreddit=subreddit,
                           subreddits=get_subreddits())


@mod.route('/delete/', methods=['GET', 'POST'])
def delete():
    """
    """
    pass


@mod.route('/edit/', methods=['GET', 'POST'])
def edit():
    """
    """
    pass




@mod.route('/<string:subreddit_name>/<int:thread_id>/<path:title>/', methods=['GET', 'POST'])
def thread_permalink(subreddit_name, thread_id, title):
    """
    """
    from base.utils.email import send_email
    send_email("test", "Great " + title, "danielecook@gmail.com")

    thread_id = thread_id or -99
    thread = Thread.query.get_or_404(int(thread_id))
    subreddit = Subreddit.query.filter_by(name=subreddit_name).first()
    return render_template('threads/permalink.html',
                           user=g.user,
                           thread=thread,
                           cur_subreddit=subreddit)

##################
# Comments Views #
##################

@mod.route('/comments/submit/', methods=['GET', 'POST'])
def submit_comment():
    """
    """
    pass

@mod.route('/comments/delete/', methods=['GET', 'POST'])
def delete_comment():
    """
    """
    pass

@mod.route('/comments/<comment_id>/', methods=['GET', 'POST'])
def comment_permalink():
    """
    """
    pass

