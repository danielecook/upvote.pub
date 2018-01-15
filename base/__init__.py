#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Written by:
Lucas Ou -- http://lucasou.com
"""
import os
from logzero import logger
from flask import Flask, render_template, url_for, g, Response
from flask_sqlalchemy import SQLAlchemy
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.routing import BaseConverter
from slugify import slugify
from base import configs
from flask_sslify import SSLify
# Ignore leading slash of urls; skips must use start of path

app = Flask(__name__, static_url_path='/static')

# Disable strict slashes
app.url_map.strict_slashes = False

STAGE, VERSION_NUM = os.environ.get('GAE_VERSION').split("-", 1)


# Setup logging
# import logging
# from google.cloud import logging as gcloud_logging
# from google.cloud.logging.handlers import CloudLoggingHandler, setup_logging
# logging_client = gcloud_logging.Client()
# log_name = f"upvote.pub-{STAGE}-{VERSION_NUM}"
# handler = CloudLoggingHandler(logging_client, name = log_name)
# setup_logging(handler, log_level=logging.INFO)

#app.logger.addHandler(handler)

app.config.from_object(getattr(configs, STAGE))

if STAGE in ['staging', 'production']:
    sslify = SSLify(app)


toolbar = DebugToolbarExtension(app)

db = SQLAlchemy(app)

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

if not app.debug:
    @app.errorhandler(404)
    def not_found(error):
        app.logger.error('404 error: %s', (error))
        return render_template('404.html', page_title="404 Error"), 404

    @app.errorhandler(500)
    def not_found(error):
        app.logger.error('500 error: %s', (error))
        return render_template('500.html', page_title="500 Error"), 500

    @app.errorhandler(Exception)
    def unhandled_exception(error):
        app.logger.error('Unhandled Exception: %s', (error))
        return render_template('404.html', page_title="Error"), 404


@app.route("/readiness_check")
@app.route("/liveness_check")
@app.route("/_ah/health")
@app.route("/ready")
def ready():
    return Response("Yep!")


from base.users.views import mod as users_module
app.register_blueprint(users_module)


from base.threads.views import mod as threads_module
app.register_blueprint(threads_module)


from base.frontends.views import mod as frontends_module
app.register_blueprint(frontends_module)


from base.apis.views import mod as apis_module
app.register_blueprint(apis_module)


from base.subreddits.views import mod as subreddits_module
app.register_blueprint(subreddits_module)


from base.sitemap.views import mod as sitemap_module
app.register_blueprint(sitemap_module)



from base.frontends.views import get_subreddits
from base.utils.misc import generate_csrf_token
@app.context_processor
def inject():
    return dict(version="v{}".format(VERSION_NUM.replace('-', '.')),
                csrf_token=generate_csrf_token,
                slugify=slugify,
                subreddits=get_subreddits(),
                user=g.get('user'))

from base.manage import (initdb, swot)


# Template filters
from base.utils import template_filters


app.debug = app.config['DEBUG']


if __name__ == '__main__':
    app.run()
