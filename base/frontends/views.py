# -*- coding: utf-8 -*-
"""
"""
from flask import (Blueprint, request, render_template, flash,
    g, session, redirect, url_for)
from werkzeug import check_password_hash, generate_password_hash
from logzero import logger
from base import db
from base import search as search_module  # don't override function name
from base.users.forms import RegisterForm, LoginForm
from base.users.models import User
from base.threads.models import Thread
from base.subreddits.models import Subreddit
from base.users.decorators import requires_login
from base.utils.user_utils import get_school
from base.subreddits.forms import subreddit_subs, sub_form

mod = Blueprint('frontends', __name__, url_prefix='')


@mod.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


def home_subreddit():
    logger.info(g.user)
    if g.user:
        subreddit_subs = g.user.subreddit_subs.get('subs')
        subs = Thread.query.order_by(db.desc(Thread.hotness), db.desc(Thread.hotness)) \
                           .filter(Subreddit.name.in_(subreddit_subs))
        #logger.info(subs)
    else:
        subs = Thread.query.order_by(db.desc(Thread.hotness), db.desc(Thread.hotness))
    return subs


def get_subreddits():
    """
    Fetch user subreddits otherwise fetch a list of defaults
    """
    if g.user:
        subreddit_subs = g.user.subreddit_subs.get('subs')
        subreddits = Subreddit.query.filter(Subreddit.name.in_(subreddit_subs))
    else:
        # Default set of subreddits
        subreddits = Subreddit.query.all()
    return subreddits


def process_thread_paginator(trending=False, rs=None, subreddit=None):
    """
    abstracted because many sources pull from a thread listing
    source (subreddit permalink, homepage, etc)
    """
    threads_per_page = 15
    cur_page = request.args.get('page') or 1
    cur_page = int(cur_page)
    thread_paginator = None

    # if we are passing in a resultset, that means we are just looking to
    # quickly paginate some arbitrary data, no sorting
    if rs:
        thread_paginator = rs.paginate(cur_page,
                                       per_page=threads_per_page,
                                       error_out=True)
        return thread_paginator

    # sexy line of code :)
    base_query = subreddit.threads if subreddit else Thread.query

    # Filter by user subs
    logger.info(g.user)
    if g.user:
        subreddit_subs = g.user.subreddit_subs.get('subs')
        base_query = base_query.join(Subreddit).filter(Subreddit.name.in_(subreddit_subs))

    if trending:
        thread_paginator = base_query.order_by(db.desc(Thread.votes)). \
        paginate(cur_page, per_page=threads_per_page, error_out=True)
    else:
        thread_paginator = base_query.order_by(db.desc(Thread.hotness)).\
                paginate(cur_page, per_page=threads_per_page, error_out=True)

    return thread_paginator


@mod.route('/')
@mod.route('/trending')
def home():
    """
    If not trending we order by creation date
    """
    trending = True if request.path.endswith('trending') else False
    page_title = "Trending" if trending else "Welcome!"
    thread_paginator = process_thread_paginator(trending=trending)

    return render_template('home.html',
                           page_title=page_title,
                           cur_subreddit=home_subreddit(),
                           thread_paginator=thread_paginator)


@mod.route('/search/', methods=['GET'])
def search():
    """
    Allows users to search threads and comments
    """
    query = request.args.get('query')
    page_title=f"Search results for '{query}'"
    rs = search_module.search(query, orderby='creation', search_title=True,
            search_text=True, limit=100)

    thread_paginator = process_thread_paginator(rs=rs)
    rs = rs.all()
    num_searches = len(rs)
    subreddits = get_subreddits()

    return render_template('home.html',
                            page_title=page_title,
                            cur_subreddit=home_subreddit(),
                            thread_paginator=thread_paginator, num_searches=num_searches)


@mod.route('/login/', methods=['GET', 'POST'])
def login():
    """
    We had to do some extra work to route the user back to
    his or her original place before logging in
    """
    if g.user:
        return redirect(url_for('frontends.home'))

    next = ''
    if request.method == 'GET':
        if 'next' in request.args:
            next = request.args['next']

    form = LoginForm(request.form)
    # make sure data is valid, but doesn't validate password is right
    if form.validate_on_submit():
        # continue where we left off if so
        user = User.query.filter_by(email=form.email.data).first()
        # we use werzeug to validate user's password
        if user and check_password_hash(user.password, form.password.data):
            # the session can't be modified as it's signed,
            # it's a safe place to store the user id
            session['user_id'] = user.id

            if 'next' in request.form and request.form['next']:
                return redirect(request.form['next'])
            return redirect(url_for('frontends.home'))

        flash('Wrong email or password', 'danger')
    return render_template("login.html", form=form, next=next)


@mod.route('/logout/', methods=['GET', 'POST'])
@requires_login
def logout():
    session.pop('user_id', None)
    return redirect(url_for('frontends.home'))


@mod.route('/register/', methods=['GET', 'POST'])
def register():
    """
    """
    next = ''
    if request.method == 'GET':
        if 'next' in request.args:
            next = request.args['next']

    form = RegisterForm(request.form)
    if form.validate_on_submit():
        # create an user instance not yet stored in the database
        user = User(username=form.username.data, email=form.email.data, \
                    password=generate_password_hash(form.password.data),
                    university=get_school(form.email.data))
        # Insert the record in our database and commit it
        db.session.add(user)
        db.session.commit()
        # Log the user in, as he now has an id
        session['user_id'] = user.id

        flash('thanks for signing up!', 'success')
        if 'next' in request.form and request.form['next']:
            return redirect(request.form['next'])
        return redirect(url_for('frontends.home'))

    return render_template("register.html", form=form, next=next)



@mod.route('/subs/', methods=['GET', 'POST'])
def view_all():
    """
    """
    if request.form:
        form = subreddit_subs(request.form)
        logger.info("FORM")
        if form.validate_on_submit():
            form_subs = form.data.get('subs')
            form_subs = list(set([x['sub_name'] for x in form_subs if x['value']]))
            g.user.subreddit_subs = {'subs': form_subs}
            flash("Updated Subs", 'success')
            db.session.commit()
    else:
        logger.info("NO FORM NO FORM FORM")
        form = subreddit_subs()
        for subreddit in Subreddit.query.all():
            sform = sub_form()
            sform.sub_name = subreddit.name
            sform.sub_group = subreddit.group
            sform.value=subreddit.name in g.user.subreddit_subs['subs']
            form.subs.append_entry(sform)


    return render_template('subreddits/subs.html',
                           cur_subreddit=None,
                           page_title='Subs',
                           form=form)
