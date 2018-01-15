# -*- coding: utf-8 -*-
"""
"""
import os
import markdown2
from flask import (Blueprint,
                   request,
                   render_template,
                   flash, g,
                   session,
                   redirect,
                   url_for,
                   abort,
                   Markup)
from werkzeug import check_password_hash, generate_password_hash
from logzero import logger
from base import db, app
from base import search as search_module  # don't override function name
from base.users.forms import RegisterForm, LoginForm
from base.users.models import User
from base.threads.models import Thread, Publication
from base.subreddits.models import Subreddit
from base.users.decorators import requires_login
from base.utils.user_utils import get_school
from base.subreddits.forms import subreddit_subs, sub_form
from base.utils.email import send_email
from base.utils.misc import random_string, validate_sort_type

mod = Blueprint('frontends', __name__, url_prefix='')


@mod.before_request
def before_request():
    g.user = None
    if session.get('user_id'):
        g.user = User.query.get(session['user_id'])


def home_subreddit():
    logger.info(g.user)
    if g.get('user'):
        subreddit_subs = g.user.subreddit_subs.get('subs')
        subs = Thread.query.order_by(db.desc(Thread.hotness), db.desc(Thread.hotness)) \
                           .filter(Subreddit.name.in_(subreddit_subs))
    else:
        subs = Thread.query.order_by(db.desc(Thread.hotness), db.desc(Thread.hotness))
    return subs


def get_subreddits():
    """
    Fetch user subreddits otherwise fetch a list of defaults
    """
    if g.get('user'):
        subreddit_subs = g.user.subreddit_subs.get('subs')
        subreddits = Subreddit.query.filter(Subreddit.name.in_(subreddit_subs))
    else:
        # Default set of subreddits
        subreddits = Subreddit.query.all()
    return subreddits


def process_thread_paginator(trending=False, rs=None, subreddit=None, sort_type='hot'):
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

    # Sorting
    if sort_type == 'hot':
        base_query = base_query.order_by(db.desc(Thread.hotness))
    elif sort_type == 'top':
        base_query = base_query.order_by(db.desc(Thread.votes))
    elif sort_type == 'comments':
        base_query = base_query.order_by(db.desc(Thread.n_comments))
    elif sort_type == 'new':
        base_query = base_query.order_by(db.desc(Thread.created_on))
    elif sort_type == 'publication_date':
        base_query = base_query.join(Publication).order_by(db.desc(Publication.pub_date))

    thread_paginator = base_query.paginate(cur_page, per_page=threads_per_page, error_out=True)

    return thread_paginator


@mod.route('/')
def home(sort_type = 'hot'):
    """
    If not trending we order by creation date
    """
    trending = True if request.path.endswith('trending') else False
    page_title = "Trending" if trending else "Frontpage"
    thread_paginator = process_thread_paginator(trending=trending)

    return render_template('home.html',
                           page_title=page_title,
                           cur_subreddit=home_subreddit(),
                           thread_paginator=thread_paginator)


@mod.route('/h/<string:page>')
def render_markdown(page):
    page = f"base/markdown/{page}.md"
    if not os.path.exists(page):
        abort(404)
    with open(page, 'r') as f:
        content = f.read()
        print(content)
        page = markdown2.markdown(content,
                                  extras = ['fenced-code-blocks',
                                                     'nofollow',
                                                     'target-blank-links',
                                                     'toc',
                                                     'tables',
                                                     'footnotes',
                                                     'metadata',
                                                     'markdown-in-html'])
    return render_template('markdown.html',
                           page=page,
                           **page.metadata)


@mod.route('/search/', methods=['GET'])
def search():
    """
    Allows users to search threads and comments
    """
    query = request.args.get('query')
    page_title=f"Search results for '{query}'"
    rs = search_module.search(query, orderby='creation', search_title=True,
            search_text=True)

    thread_paginator = process_thread_paginator(rs=rs)
    #rs = rs.all()
    num_searches = rs.count()
    subreddits = get_subreddits()

    return render_template('home.html',
                            page_title=page_title,
                            cur_subreddit=home_subreddit(),
                            thread_paginator=thread_paginator,
                            num_searches=num_searches)


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


@mod.route('/confirm-email/<string:token>')
def confirm_email(token):
    """
        Confirm user email
    """
    user = User.query.filter_by(email_token=token).first()
    if user.email_token == token:
        user.email_verified = True
    db.session.commit()
    flash("Thank you for confirming your email! You can now submit and comment.", 'success')
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
        user = User(username=form.username.data,
                    email=form.email.data, \
                    password=generate_password_hash(form.password.data),
                    university=get_school(form.email.data),
                    email_token=random_string())
        # Insert the record in our database and commit it
        db.session.add(user)
        email_confirm_link = url_for('frontends.confirm_email', token = user.email_token)
        email_response = send_email("Confirm upvote.pub email",
                                    """Please visit the link below to confirm your email:\n\n{}{}""".format(request.url_root.strip("/"), email_confirm_link),
                                    user.email)
        # Log the user in, as he now has an id
        db.session.commit()
        session['user_id'] = user.id
        flash('Thanks for signing up! Please confirm your email by following the link sent in the confirmation email.', 'success')
        if 'next' in request.form and request.form['next']:
            return redirect(request.form['next'])
        return redirect(url_for('frontends.home'))

    return render_template("register.html", form=form, next=next)


@mod.route('/subs/', methods=['GET', 'POST'])
def view_all():
    """
    """
    subreddit_list = Subreddit.query.all()
    form = None
    if g.user:
        if request.form:
            form = subreddit_subs(request.form)
            if form.validate_on_submit():
                form_subs = form.data.get('subs')
                form_subs = list(set([x['sub_name'] for x in form_subs if x['value']]))
                g.user.subreddit_subs = {'subs': form_subs}
                flash("Updated Subs", 'success')
                db.session.commit()
        else:
            form = subreddit_subs()
            for subreddit in subreddit_list:
                sform = sub_form()
                sform.sub_name = subreddit.name
                sform.sub_group = subreddit.group
                if g.user:
                    sform.value=subreddit.name in g.user.subreddit_subs['subs']
                form.subs.append_entry(sform)


    return render_template('subreddits/subs.html',
                           cur_subreddit=None,
                           page_title='subs',
                           form=form,
                           subreddit_list=subreddit_list)
