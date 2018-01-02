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

