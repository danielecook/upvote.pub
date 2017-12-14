#!/usr/bin/env python2.7
"""
/shell.py will allow you to get a console and enter commands within your flask environment.
"""
import os
import sys
import readline
from pprint import pprint

from flask import *

sys.path.insert(0, '/home/lucas/www/reddit.lucasou.com/reddit-env/base')
from base import *
from base.users.models import *
from base.threads.models import *
from base.subreddits.models import *
from base.threads.models import thread_upvotes, comment_upvotes

os.environ['PYTHONINSPECT'] = 'True'
