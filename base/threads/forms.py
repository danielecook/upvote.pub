# -*- coding: utf-8 -*-
"""
"""
import arrow
from flask import g
from base.utils.pubs import id_type
from base.threads.models import Thread
from flask_wtf import Form
from wtforms import TextField, TextAreaField, ValidationError
from wtforms.validators import Required
from base.users.models import User


def is_valid_id(form, field):
    if field.data:
        pub_id_type, pub_id = id_type(field.data.strip())
        if not pub_id_type:
            raise ValidationError("Invalid publication ID.")
    # Throttle user if they have submitted too frequently.
    user_id = g.user.id
    since = arrow.utcnow() - arrow.utcnow().shift(hours=-2).datetime
    submission_count = Thread.query.filter(Thread.user_id == user_id, Thread.created_on > since).count()
    # Limit submissions for general users only
    if submission_count > 5 and g.user.role == 0:
        raise ValidationError("You've been submitting too much.")
    if g.user.email_verified is not True:
        raise ValidationError("You must verify your email to submit")


class submit_pub_form(Form):
    pub_id = TextField('pub ID', [Required(), is_valid_id])
    text = TextAreaField('Comments') # [Length(min=5, max=THREAD.MAX_BODY)]