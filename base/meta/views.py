# -*- coding: utf-8 -*-
"""
"""
from logzero import logger
from flask import (Blueprint, request, render_template, flash, g, session,
                   redirect, url_for, abort)

mod = Blueprint('meta', __name__, url_prefix='/r')

#################
# Threads Views #
#################

@mod.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])



@mod.route('/tos/', methods=['GET', 'POST'])
def tos(subreddit_name=None):
    """
        Terms of Service
    """
    page_title="Terms of Service"
    
    return render_template('meta/tos.html', page_title=page_title)

