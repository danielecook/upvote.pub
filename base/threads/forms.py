# -*- coding: utf-8 -*-
"""
"""
from flask import url_for
from base.utils.pubs import id_type
from base.threads.models import Thread
from flask_wtf import Form
from wtforms import TextField, TextAreaField, ValidationError
from wtforms.validators import Required, URL


def is_valid_id(form, field):
    if field.data:
        pub_id_type, pub_id = id_type(field.data.strip())
        if not pub_id_type:
            raise ValidationError("Invalid publication ID.")


class submit_pub_form(Form):
    pub_id = TextField('pub ID', [Required(), is_valid_id])
    text = TextAreaField('Comments') # [Length(min=5, max=THREAD.MAX_BODY)]