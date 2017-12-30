# -*- coding: utf-8 -*-
"""
"""
from flask import (Blueprint,
                   render_template,
                   g,
                   session,
                   abort)

from base.users.models import User
from base.frontends.views import get_subreddits


mod = Blueprint('users', __name__, url_prefix='/users')


@mod.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@mod.route('/<username>/')
def user_profile(username=None):
    if not username:
        abort(404)
    user = User.query.filter_by(username=username).first()
    if not user:
        abort(404)
    return render_template('users/profile.html',
                           current_user=user,
                           cur_subreddit=None,
                           page_title=user.username,
                           page_subtitle=user.university,
                           subreddits = get_subreddits())

