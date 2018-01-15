import arrow
import string
import random
from flask import session


def now():
    return arrow.utcnow().datetime


def random_string(size=18, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))


def generate_csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = random_string()
    return session['csrf_token']


def validate_sort_type(sort_type):
    if sort_type not in ['hot', 'top', 'new', 'comments', 'publication_date']:
        return 'hot'
    return sort_type