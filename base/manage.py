# -*- coding: utf-8 -*-
"""
All code for scraping images and videos from posted
links go in this file.
"""
import random
import requests
import click
import time
from click import secho
import os
import sys
import shutil
import readline
import pickle
import redis
import IPython
from base import configs
from collections import defaultdict
from subprocess import Popen, PIPE

from flask import *
from werkzeug import check_password_hash, generate_password_hash

from base import db
from base.users.models import *
from base.threads.models import *
from base.subreddits.models import *
from base.utils.pubs import fetch_pub
from base.utils.misc import random_string

from base.utils.query import get_or_create
from base import app
from base.utils.gcloud import get_item
from base.subreddits.constants import BASE_SUBREDDITS



@app.cli.command()
@click.argument('env', type=click.Choice(['local', 'staging', 'production']))
def initdb(env):
    """Initialize the ID database"""
    # Mock environment
    app.config.from_object(getattr(configs, env))

    # Remove socket connection
    if env in ['staging', 'production']:
        remote_url = get_item('credential', f"sql-{env}").get('remote_url')
        secho(remote_url, fg='green')
        app.config['SQLALCHEMY_DATABASE_URI'] = remote_url

    secho(f"Init the db -- {env}", fg='green')
    secho(app.config['SQLALCHEMY_DATABASE_URI'])
    db.drop_all()
    db.create_all()
    first_user = User(username='dec',
                      email='dec@u.northwestern.edu',
                      email_verified=True,
                      password=generate_password_hash('london!88'),
                      university='Northwestern University')

    db.session.add(first_user)
    db.session.commit()

    # Install base set of subreddits
    for group, subreddits in BASE_SUBREDDITS.items():
        for subreddit in subreddits: 
            if type(subreddit) is tuple:
                sub = Subreddit(name=subreddit[0],
                                description=subreddit[1], 
                                group=group,
                                admin_id=first_user.id)
            else:
                sub = Subreddit(name=subreddit, 
                          group=group,
                          admin_id=first_user.id)
            db.session.add(sub)
    db.session.commit()


@app.cli.command()
@click.argument('env', type=click.Choice(['local', 'staging', 'production']))
@click.argument('name')
@click.argument('group')
def create_subreddit(env, name, group):
    """
        Add a new subreddit
    """
    app.config.from_object(getattr(configs, env))
    secho(f"Adding subreddit -- {env}", fg='green')
    add_sub = Subreddit(name=name, group=group, admin_id=1)

    db.session.add(add_sub)
    db.session.commit()


@app.cli.command()
def worker():
    """
        Run the huey worker
    """
    comm=['huey_consumer.py','-w','4','--logfile', 'tasks.log', 'base.async.tasks.huey']
    Popen(comm).communicate()


@app.cli.command()
@click.argument('env', type=click.Choice(['locoal', 'staging', 'production']))
def remote_redis(env):
    """
        Launches a python terminal with redis available
    """
    r = redis.Redis(**get_item('credential', 'redis-{}'.format(env)))
    IPython.embed(user_ns=locals())


@app.cli.command()
def swot():
    """
        Generate school affiliation database
    """
    secho('Generating school/university affiliations', fg='green')
    out, err = Popen(['git','clone','https://github.com/leereilly/swot'],
                      stdout=PIPE,
                      stderr=PIPE).communicate()
    school_directory = defaultdict()
    for root, dirs, files in os.walk("swot/lib/domains"):
        domain_root = root.split("/")[3:]
        current_dir = school_directory
        for i in domain_root:
            if i not in current_dir.keys():
                current_dir[i] = defaultdict()
            current_dir = current_dir[i]
        for file in files:
            domain = file
            if file != ".DS_Store":
                with open(root + "/" + file, 'r',  encoding="utf-8") as f:
                    school = f.read().strip().encode('utf-8')
                current_dir[domain] = school.decode('utf-8').split(" In ")[0].strip()

    shutil.rmtree("swot")
    with open('base/static/data/school_directory.pkl', 'wb') as f:
        f.write(pickle.dumps(school_directory))


@app.cli.command()
@click.argument('env', type=click.Choice(['local', 'staging', 'production']))
@click.argument('username')
@click.argument('sub')
@click.argument('pub_id')
def create_pub(env, username, sub, pub_id):
    """
        For debugging purposes really
    """
    app.config.from_object(getattr(configs, env))

    # Remove socket connection
    if env in ['staging', 'production']:
        remote_url = get_item('credential', f"sql-{env}").get('remote_url')
        secho(remote_url, fg='green')
        app.config['SQLALCHEMY_DATABASE_URI'] = remote_url

    pub_data = fetch_pub(str(pub_id))
    logger.info(f"Adding {pub_data.pub_title}")
    if pub_data:
        user = User.query.filter_by(username=username).first()
        if not user:
            VARS = {'username': username,
                    'email': "FAKE__{}@FAKE.edu".format(random_string()),
                    'password': generate_password_hash('WZRfEsxjLYieTHbonP7JWig3FEBRAFCYthnJdph7fd9frs2BejHsbXWZGYnFmazT'),
                    'university': ""}
            user, created = get_or_create(User, **VARS)
        sub_id = Subreddit.query.filter_by(name=sub).first().id
        created_on = arrow.utcnow().shift(seconds=-random.randint(1,350000)).datetime
        thread = Thread(user_id=user.id,
                        subreddit_id=sub_id,
                        publication_id=pub_data.id,
                        created_on=created_on,
                        updated_on=created_on)

        db.session.add(thread)
        db.session.commit()

