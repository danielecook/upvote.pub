# -*- coding: utf-8 -*-
"""
"""
from flask_wtf import Form, RecaptchaField
from wtforms import TextField, PasswordField, BooleanField
from wtforms.validators import Required, EqualTo, Email
from wtforms import ValidationError
from base.utils.user_utils import get_school
from base.users.models import User


def school_email(form, field):
    if field.data:
        school = get_school(field.data.strip())
        if not school:
            raise ValidationError("You must use an academic email address to signup.")


def username_check(form, field):
    user = User.query.filter_by(username=field.data.strip()).first()
    if user:
        raise ValidationError("That username is taken.")


def email_check(form, field):
    user = User.query.filter_by(email=field.data.strip()).first()
    if user:
        raise ValidationError("That email is already registered.")




class LoginForm(Form):
    email = TextField('Email address', [Required(), Email()])
    password = PasswordField('Password', [Required()])


class RegisterForm(Form):
    username = TextField('NickName', [Required(), username_check])
    email = TextField('Email address', [Required(), Email(), school_email, email_check])
    password = PasswordField('Password', [Required()])
    confirm = PasswordField('Repeat Password', [
        Required(),
        EqualTo('password', message='Passwords must match')
    ])
    accept_tos = BooleanField('I accept the Terms of Service', [Required()])
    #recaptcha = RecaptchaField()

