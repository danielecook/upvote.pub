# -*- coding: utf-8 -*-
"""
"""
import glob
import os
from flask import (Blueprint,
                   render_template,
                   url_for)
from slugify import slugify
from base.threads.models import Thread
from base.subreddits.models import Subreddit
from base.users.models import User
from base import app
import arrow
from flask import make_response

mod = Blueprint('sitemap', __name__)


IGNORE_RULES = ['/_ah/health',
                '/liveness_check',
                '/sitemap.xml',
                '/readiness_check',
                '/ready',
                '/logout/',
                '/search/',
                '/login/']

# a route for generating sitemap.xml
@mod.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """Generate sitemap.xml. Makes a list of urls and date modified."""
    pages = []
    ten_days_ago = arrow.utcnow().shift(days=-10).datetime.isoformat()
    # static pages
    for rule in app.url_map.iter_rules():
        if rule.rule not in IGNORE_RULES:
            if "GET" in rule.methods and len(rule.arguments)==0:
                pages.append({"url": rule.rule,
                              "changefreq": 'daily',
                              "priority": 0.5})
    
    # Markdown
    markdown_pages = [os.path.basename(x).replace(".md", "")  for x in glob.glob("base/markdown/*")]
    for md in markdown_pages:
        url=url_for('frontends.render_markdown',
                    page=md)
        modified_time = arrow.get(os.stat(f"base/markdown/{md}.md").st_mtime).datetime.isoformat()
        change_freq = 'weekly'
        priority = 0.5
        pages.append({"url": url,
                      "lastmod": modified_time,
                      "changefreq": change_freq,
                      "priority": priority})

    # subs
    subs = Subreddit.query.all()
    for sub in subs:
        url=url_for('subreddits.permalink',
                    subreddit_name=sub.name)
        change_freq = 'hourly'
        priority = 0.9
        pages.append({"url": url,
                      "changefreq": change_freq,
                      "priority": priority})
    # threads
    threads = Thread.query.order_by(Thread.created_on).all()
    for thread in threads:
        url=url_for('threads.thread_permalink',
                    thread_id=thread.id,
                    subreddit_name=thread.subreddit.name,
                    title=slugify(thread.publication.pub_title))
        change_freq = 'daily'
        priority = 0.8
        pages.append({"url": url,
                      "changefreq": change_freq,
                      "priority": priority})

    # user model pages
    users=User.query.order_by(User.created_on).all()
    for user in users:
        url=url_for('users.user_profile', username=user.username)
        modified_time = user.created_on.date().isoformat()
        change_freq = 'monthly'
        priority = 0.5
        pages.append({"url": url,
                      "lastmod": modified_time,
                      "changefreq": change_freq,
                      "priority": priority})

    sitemap_xml = render_template('sitemap.xml', pages=pages)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response