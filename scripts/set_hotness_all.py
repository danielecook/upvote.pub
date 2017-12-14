#!/usr/bin/env python2.7
"""
"""
import os
import sys
sys.path.insert(0, '/home/lucas/www/reddit.lucasou.com/reddit-env/base')
import readline
from pprint import pprint

from flask import *
from base import *

from base.users.models import *
from base.threads.models import *
from base.subreddits.models import *
from base.threads.models import thread_upvotes, comment_upvotes

threads = Thread.query.all()
for thread in threads:
    thread.set_hotness()

import time
print 'Hotness values have been computed for all threads without error on', \
    time.strftime("%H:%M:%S"), \
    time.strftime("%d/%m/%Y")
