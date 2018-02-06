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
from base.utils.misc import validate_sort_type
from werkzeug.contrib.atom import AtomFeed
from slugify import slugify

mod = Blueprint('subreddits', __name__, url_prefix='/r')

###################
# Subreddit Views #
###################

@mod.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


# atom Feed
@mod.route('/<subreddit_name>/.atom', methods=['GET'])
@mod.route('/<subreddit_name>/sort/<string:sort_type>/.atom', methods=['GET'])
@mod.route('/<subreddit_name>/.xml', methods=['GET'])
@mod.route('/<subreddit_name>/sort/<string:sort_type>/.xml', methods=['GET'])
@mod.route('/<subreddit_name>/.rss', methods=['GET'])
@mod.route('/<subreddit_name>/sort/<string:sort_type>/.rss', methods=['GET'])
def atom_feed(subreddit_name=None, sort_type="hot"):
    """
    """
    feed = AtomFeed(title=f"upvote.pub > {subreddit_name}",
                    feed_url=request.url, url=request.url_root)

    # Pseudo frontpage subreddit --> None
    if subreddit_name == 'frontpage':
        subreddit_name = None
    subreddit = Subreddit.query.filter_by(name=subreddit_name).first()
    trending = True if request.args.get('trending') else False
    thread_paginator = process_thread_paginator(trending=trending,
                                                subreddit=subreddit,
                                                sort_type=sort_type)
    for thread in thread_paginator.items:
        thread_url = url_for('threads.thread_permalink',
                             subreddit_name=thread.subreddit.name,
                             thread_id=thread.id,
                             title=slugify(thread.publication.pub_title),
                             _external=True)
        feed.add(thread.publication.pub_title, thread.publication.pub_abstract,
                 content_type='html',
                 author=thread.publication.pub_authors,
                 url=thread_url,
                 updated=thread.created_on,
                 published=thread.updated_on)
    return feed.get_response()



@mod.route('/<subreddit_name>/', methods=['GET'])
@mod.route('/<subreddit_name>/sort/<string:sort_type>')
def permalink(subreddit_name="", sort_type="hot"):
    """
    """
    atom_url = url_for('subreddits.atom_feed',
                       subreddit_name=subreddit_name,
                       sort_type=sort_type,
                       _external=True)
    sort_type = validate_sort_type(sort_type)
    subreddit = Subreddit.query.filter_by(name=subreddit_name).first()
    if not subreddit:
        abort(404)

    trending = True if request.args.get('trending') else False
    thread_paginator = process_thread_paginator(trending=trending,
                                                subreddit=subreddit,
                                                sort_type=sort_type)
    subreddits = get_subreddits()

    return render_template('home.html',
                           atom_url=atom_url,
                           thread_paginator=thread_paginator,
                           subreddits=subreddits,
                           cur_subreddit=subreddit,
                           page_title=subreddit.name,
                           sort_type=sort_type)

