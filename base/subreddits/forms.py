# -*- coding: utf-8 -*-
"""
"""
from base.threads import constants as THREAD
from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField
from wtforms.validators import Required, URL, Length

class SubmitForm(Form):
    name = TextField('Name your community!', [Required()])
    desc = TextAreaField('Description of subreddit!', [Required()])
