# -*- coding: utf-8 -*-
"""
"""
from flask import (Blueprint, request, render_template, flash, g,
        session, redirect, url_for, abort)
from base.frontends.views import get_subreddits, process_thread_paginator
from base.subreddits.forms import SubmitForm
from base.subreddits.models import Subreddit
from base.threads.models import Thread
from base.users.models import User
from base import db

mod = Blueprint('subreddits', __name__, url_prefix='/r')

###################
# Subreddit Views #
###################

@mod.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@mod.route('/subreddits/submit/', methods=['GET', 'POST'])
def submit():
    """
    """
    if g.user is None:
        flash('You must be logged in to submit subreddits!', 'danger')
        return redirect(url_for('frontends.login', next=request.path))

    form = SubmitForm(request.form)
    user_id = g.user.id

    if form.validate_on_submit():
        name = form.name.data.strip()
        desc = form.desc.data.strip()

        subreddit = Subreddit.query.filter_by(name=name).first()
        if subreddit:
            flash('subreddit already exists!', 'danger')
            return render_template('subreddits/submit_subreddit.html', form=form, user=g.user,
                subreddits=get_subreddits())
        new_subreddit = Subreddit(name=name, desc=desc, admin_id=user_id)

        return render_template('subreddits/submit_subreddit.html', form=form)

        db.session.add(new_subreddit)
        db.session.commit()

        return redirect(url_for('subreddits.permalink', subreddit_name=new_subreddit.name))
    return render_template('subreddits/submit_subreddit.html',
                           form=form,
                           page_title='Submit!')


@mod.route('/delete/', methods=['GET', 'POST'])
def delete():
    """
    """
    pass



@mod.route('/<subreddit_name>/', methods=['GET'])
def permalink(subreddit_name=""):
    """
    """
    subreddit = Subreddit.query.filter_by(name=subreddit_name).first()
    if not subreddit:
        abort(404)

    trending = True if request.args.get('trending') else False
    thread_paginator = process_thread_paginator(trending=trending, subreddit=subreddit)
    subreddits = get_subreddits()

    return render_template('home.html',
                           thread_paginator=thread_paginator,
                           subreddits=subreddits,
                           cur_subreddit=subreddit,
                           page_title=subreddit.name)

