# -*- coding: utf-8 -*-
"""
"""
from flask import (Blueprint, request, render_template, flash, g, session,
                   redirect, url_for, abort)
from base.threads.forms import submit_pub_form
from base.threads.models import Thread
from base.users.models import User
from base.subreddits.models import Subreddit
from base.frontends.views import get_subreddits
from base import db
from base.utils.pubs import fetch_pub

mod = Blueprint('threads', __name__, url_prefix='/threads')

#################
# Threads Views #
#################


@mod.context_processor
def inject():
    return dict(subreddits=get_subreddits(),
                user=g.user)



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
    if form.validate_on_submit():
        # Fetch data from publication
        pub_id = form.pub_id.data
        pub_data = fetch_pub(pub_id)
        text = form.text.data.strip()

        # Switch to using a validator for pub data - 
        # store results in redis...?
        if not pub_data:
            subreddits = get_subreddits()
            return render_template('threads/submit_post.html', form=form, user=g.user,
                cur_subreddit=subreddit.name)
        
        thread = Thread(text=text, user_id=user_id, subreddit_id=subreddit.id, **pub_data)

        db.session.add(thread)
        db.session.commit()
        thread.set_hotness()

        flash('thanks for submitting!', 'success')
        return redirect(url_for('subreddits.permalink', subreddit_name=subreddit.name))
    return render_template('threads/submit_post.html',
                           form=form,
                           page_title='Submit a new pub/manuscript',
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

