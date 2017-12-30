# -*- coding: utf-8 -*-
"""
"""
from base.threads import constants as THREAD
from flask_wtf import Form
from wtforms import FormField, StringField, HiddenField, TextField, TextAreaField, FieldList, BooleanField
from wtforms.validators import Required, URL, Length, optional


class sub_form(Form):
    sub_name = HiddenField('sub_name')
    sub_group = HiddenField('sub_group')
    value = BooleanField('sub')


class subreddit_subs(Form):
    subs = FieldList(FormField(sub_form), [Required()])


class SubmitForm(Form):
    name = TextField('Name your community!', [Required()])
    desc = TextAreaField('Description of subreddit!', [Required()])
