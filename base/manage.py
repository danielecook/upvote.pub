# -*- coding: utf-8 -*-
"""
All code for scraping images and videos from posted
links go in this file.
"""
import requests
import click
import os
import sys
import readline
from pprint import pprint

from flask import *
from werkzeug import check_password_hash, generate_password_hash

from base import db
from base.users.models import *
from base.threads.models import *
from base.subreddits.models import *

from base import app

base_subreddits = {'biology': ['biochemistry',
                               'bioengineering',
                               'bioinformatics',
                               'biophysics',
                               'evolution',
                               'genetics',
                               'genomics',
                               'molecular_biology',
                               'systems_biology'],
                   'statistics': ['stat_application',
                                  'stat_computation',
                                  ('ml', 'machine_learning'),
                                  'stat_methods']
                  }


@app.cli.command()
def initdb():
    """Initialize the ID database"""
    click.echo('Init the db')
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
def create_subreddit():
    first_subreddit = Subreddit(name='frontpage', desc='Welcome to Reddit! Here is our homepage.',
            admin_id=first_user.id)

    db.session.add(first_subreddit)
    db.session.commit()