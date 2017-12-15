# -*- coding: utf-8 -*-
"""
"""
from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField
from wtforms.validators import Required, URL


class submit_pub_form(Form):
    pub_id = TextField('DOI / PMID', [Required()])
    text = TextAreaField('Body text') # [Length(min=5, max=THREAD.MAX_BODY)]