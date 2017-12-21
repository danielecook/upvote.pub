# -*- coding: utf-8 -*-
"""
"""
from flask import url_for
from base.utils.pubs import id_type
from base.threads.models import Thread
from flask.ext.wtf import Form
from wtforms import TextField, TextAreaField, ValidationError
from wtforms.validators import Required, URL


def is_valid_id(form, field):
    if field.data:
        if not id_type(field.data):
            raise ValidationError("Invalid publication ID.")


def is_unique_submission(form, field):
    if field.data:
        thread = Thread.query.filter_by(pub_doi=field.data).first()
        if thread:
            thread_url =  url_for('threads.thread_permalink',
                                  subreddit_name = thread.subreddit.name,
                                  thread_id = thread.id,
                                  title=thread.pub_title[:100].replace(" ", "_"))
            raise ValidationError(f"That <a href='{thread_url}'>pub</a> has already been submitted.")


class submit_pub_form(Form):
    pub_id = TextField('pub ID', [Required(), is_valid_id, is_unique_submission])
    text = TextAreaField('Body text') # [Length(min=5, max=THREAD.MAX_BODY)]