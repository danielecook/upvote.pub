# -*- coding: utf-8 -*-
import datetime
import os
from redis import Redis
from datetime import timedelta
from redis import Redis, ConnectionPool
from gcloud import datastore
from base.utils.gcloud import get_item
from logzero import logger

logger.info("Loading Config")
STAGE, VERSION_NUM = os.environ.get('GAE_VERSION').split("-", 1)


class base_config(object):
    JSON_SORT_KEYS = False
    BRAND = "upvote.pub"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    try:
        SENDGRID_API_KEY = get_item('credential', 'sendgrid')
    except:
        SENDGRID_API_KEY = None
    STATIC_FOLDER = '/static'


# Use conditional logic here to prevent app from loading datastore items
# when not using that config.

class local(base_config):
    ONLINE = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG = True
    TESTING = True
    CSRF_ENABLED = True
    CSRF_SESSION_KEY = "eNr24cD79[KpDe;vbZ9t"
    HOST = "docker.for.mac.localhost" if os.environ.get('IS_DOCKER') else "127.0.0.1"
    SQLALCHEMY_DATABASE_URI = f"mysql://root@{HOST}/upvote"
    REDIS_HOST = HOST
    REDIS_PORT = 6379
    REDIS_DB_NAME = 0
    REDIS_CONNECTION_POOL = ConnectionPool(host=REDIS_HOST,
                                           port=REDIS_PORT,
                                           db=REDIS_DB_NAME)
    REDIS_DB = Redis(connection_pool=REDIS_CONNECTION_POOL)
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SECRET_KEY = 'secret'
    SESSION_COOKIE_PATH='/'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_NAME = 'upvote_pub_debug'
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(31)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    PERMANENT_SESSION_LIFETIME = timedelta(days=1000)
    SQLALCHEMY_ECHO = False


class staging(base_config):
    TESTING = True
    TRAP_HTTP_EXCEPTIONS = True
    TRAP_BAD_REQUEST_ERRORS = True
    DEBUG = False
    SESSION_COOKIE_NAME = 'upvote-staging'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SQLALCHEMY_ECHO = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    CSRF_SESSION_KEY = get_item('credential', 'csrf').get('key')
    SECRET_KEY = get_item('credential', 'secret-staging').get('secret')
    SQLALCHEMY_DATABASE_URI = get_item('credential', 'sql-staging').get('url')
    REDIS_CONNECTION_POOL = ConnectionPool(**get_item('credential', 'redis-staging'))
    REDIS_DB = Redis(connection_pool=REDIS_CONNECTION_POOL)


class production(base_config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    TESTING = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    SESSION_COOKIE_NAME = 'upvote'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    CSRF_SESSION_KEY = get_item('credential', 'csrf').get('key')
    SECRET_KEY = get_item('credential', 'secret-production').get('secret')
    SQLALCHEMY_DATABASE_URI = get_item('credential', 'sql-production').get('url')
    REDIS_CONNECTION_POOL = ConnectionPool(**get_item('credential', 'redis-production'))
    REDIS_DB = Redis(connection_pool=REDIS_CONNECTION_POOL)

