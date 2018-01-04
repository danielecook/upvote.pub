# -*- coding: utf-8 -*-
"""
All code for scraping images and videos from posted
links go in this file.
"""
import requests
import click
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

from base import app
from base.utils.gcloud import get_item


base_subreddits = {'biology': ['biochemistry',
                               'bioengineering',
                               'bioinformatics',
                               'biophysics',
                               'evolution',
                               'genetics',
                               'genomics',
                               'molecular_biology',
                               'systems_biology'],
                   'statistics': ['statistics',
                                  'machine_learning']
                  }


@app.cli.command()
@click.argument('env', type=click.Choice(['local', 'staging', 'production']))
def initdb(env):
    """Initialize the ID database"""
    app.config.from_object(getattr(configs, env))
    secho(f"Init the db -- {env}", fg='green')
    db.drop_all()
    db.create_all()
    first_user = User(username='dec', email='dec@u.northwestern.edu', \
                      password=generate_password_hash('d'),
                      university='Northwestern University')

    db.session.add(first_user)
    db.session.commit()

    # Install base set of subreddits
    for group, subreddits in base_subreddits.items():
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
@click.argument('env', type=click.Choice(['local', 'staging', 'production']))
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
def create_pub():
    """
        For debugging purposes really
    """
    for i in range(1000,3000):
        pub_data = fetch_pub(str(i))
        if pub_data:
            thread = Thread(user_id=1, subreddit_id=1, **pub_data)

            db.session.add(thread)
            db.session.commit()
