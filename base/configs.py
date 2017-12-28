# -*- coding: utf-8 -*-
import datetime
from redis import Redis
from datetime import timedelta
from redis import Redis, ConnectionPool


class base_config(object):
    JSON_SORT_KEYS = False
    BRAND = "upvote.pub"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    

class local(base_config):
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    RECAPTCHA_USE_SSL = False
    RECAPTCHA_PUBLIC_KEY = ''
    RECAPTCHA_PRIVATE_KEY = ''
    RECAPTCHA_OPTIONS = {'theme': 'white'}

    DEBUG = True
    CSRF_ENABLED = True
    CSRF_SESSION_KEY = "eNr24cD79[KpDe;vbZ9t"
    SQLALCHEMY_DATABASE_URI = 'mysql://root@127.0.0.1/upvote'
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_DB_NAME = 0
    REDIS_CONNECTION_POOL = ConnectionPool(host=REDIS_HOST,
                                           port=REDIS_PORT,
                                           db=REDIS_DB_NAME)
    REDIS_DB = Redis(connection_pool=REDIS_CONNECTION_POOL)
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"  # For cache
    REDIS_USER = ""
    REDIS_PASSWORD = None
    REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}"  # For cache
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SECRET_KEY = 's'
    SESSION_COOKIE_PATH='/'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_NAME = 'flask_session'
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(31)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    PERMANENT_SESSION_LIFETIME = timedelta(days=1000)


class TestConfig(object):
    SQLALCHEMY_DATABASE_URL = 'postgresql+psycopg2://xxxxxxxxxxxxxxxxx'
    SQLALCHEMY_ECHO = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


class ProductionConfig(object):
    SQLALCHEMY_ECHO = False
    DEBUG = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
