#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Written by:
Lucas Ou -- http://lucasou.com
"""
from flask import Flask, render_template, url_for, g
from flask_sqlalchemy import SQLAlchemy
from werkzeug.routing import BaseConverter
from slugify import slugify

app = Flask(__name__, static_url_path='/static')
app.config.from_object('config')

db = SQLAlchemy(app)

class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def not_found(error):
    return render_template('500.html'), 500



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


from base.frontends.views import get_subreddits
@app.context_processor
def inject():
    return dict(slugify=slugify,
                subreddits=get_subreddits(),
                user=g.user)

from base.manage import (initdb)


def custom_render(template, *args, **kwargs):
    """
    custom template rendering including some base vars
    """
    return render_template(template, *args, **kwargs)

app.debug = app.config['DEBUG']


if __name__ == '__main__':
    app.run()
