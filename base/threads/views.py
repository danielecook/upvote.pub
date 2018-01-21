# -*- coding: utf-8 -*-
"""
"""
from logzero import logger
from flask import (Blueprint, request, render_template, flash, g, session,
                   redirect, url_for, abort)
from slugify import slugify
from base.threads.forms import submit_pub_form, submit_pub_bookmarklet_form
from base.threads.models import Thread, Publication, Publication_Download
from base.users.models import User
from base.subreddits.models import Subreddit
from base.frontends.views import get_subreddits
from base import db
from base.utils.pubs import fetch_pub
from base.utils.pub_ids import id_type, get_publication



mod = Blueprint('threads', __name__, url_prefix='/r')

#################
# Threads Views #
#################


@mod.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])


@mod.route('/new', methods=['GET', 'POST'])
@mod.route('/<subreddit_name>/submit/', methods=['GET', 'POST'])
def submit(subreddit_name=None):
    """
    """
    if g.user is None:
        flash('You must be logged in to submit posts!', 'danger')
        return redirect(url_for('frontends.login', next=request.path))

    user_id = g.user.id

    if subreddit_name:
        is_bookmarklet=False
        subreddit = Subreddit.query.filter_by(name=subreddit_name).first()
        form = submit_pub_form(request.form)
        submit_title = subreddit_name
        if not subreddit:
            abort(404)
    else:
        # Bookmarklet
        is_bookmarklet=True
        url = request.args.get('url') or ""
        form = submit_pub_bookmarklet_form(request.form, pub_id=url)
        form.set_choices()

        if form.subreddit.data:
            subreddit = Subreddit.query.filter_by(id=form.subreddit.data).first()
            if subreddit:
                subreddit_name = subreddit.name
                submit_title = subreddit_name
        else:
            subreddit = None
            submit_title = "upvote.pub!"


    # Check if pub has already been submitted
    if form.pub_id.data and subreddit_name:
        publication = get_publication(form.pub_id.data)
        if publication:
            for thread in publication.threads:
                if thread.subreddit.name == subreddit_name:
                    flash(f"That pub has already been submitted to {subreddit.name}!", 'warning')
                    return redirect(url_for('threads.thread_permalink',
                                            thread_id=thread.id,
                                            subreddit_name=subreddit.name,
                                            title=slugify(publication.pub_title)))

    if form.validate_on_submit():
        # Fetch data from publication
        pub_id = form.pub_id.data
        pub_item = fetch_pub(pub_id)

        if not pub_item:
            flash("Could not find a pub with the ID: '{}'".format(form.pub_id.data), 'danger')
            return render_template('threads/submit_post.html',
                                   page_title=f"Submit to {submit_title}",
                                   form=form,
                                   cur_subreddit=subreddit.name)


        thread = Thread(user_id=user_id, subreddit_id=subreddit.id, publication_id=pub_item.id)

        db.session.add(thread)
        db.session.commit()
        flash("Thank you for submitting!", "success")
        return redirect(url_for('threads.thread_permalink',
                                thread_id=thread.id,
                                subreddit_name=thread.subreddit.name,
                                title=slugify(pub_item.pub_title)))
    return render_template('threads/submit_post.html',
                           form=form,
                           page_title=f"Submit to {submit_title}",
                           subreddits=get_subreddits(),
                           is_bookmarklet=is_bookmarklet)


@mod.route('/<string:subreddit_name>/<int:thread_id>/<path:title>/', methods=['GET', 'POST'])
def thread_permalink(subreddit_name, thread_id, title):
    """
    """

    thread_id = thread_id or -99
    thread = Thread.query.get_or_404(int(thread_id))
    subreddit = Subreddit.query.filter_by(name=subreddit_name).first()
    return render_template('threads/permalink.html',
                           html_title=thread.publication.pub_title,
                           user=g.user,
                           thread=thread,
                           cur_subreddit=subreddit)


@mod.route("/download/<path:pub_id>")
def download_pdf(pub_id):
    """
        Used to track whether a publication has been downloaded - marking a thread as visited.
    """
    publication = get_publication(pub_id)
    if not publication:
        abort(404)
    if g.user:
        publication.mark_downloaded(g.user.id)

    pub_url = publication.pub_pdf_url
    if pub_url and pub_url != 'searching':
        return redirect(pub_url, code=302)
    else:
        abort(404)
