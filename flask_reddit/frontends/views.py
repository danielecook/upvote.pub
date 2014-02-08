# -*- coding: utf-8 -*-
"""
"""
from flask import Blueprint, request, render_template, flash, g, session, redirect, url_for
from werkzeug import check_password_hash, generate_password_hash

from flask_reddit import db
from flask_reddit.users.forms import RegisterForm, LoginForm
from flask_reddit.users.models import User
from flask_reddit.threads.models import Thread
from flask_reddit.users.decorators import requires_login

mod = Blueprint('frontends', __name__, url_prefix='')

@mod.route('/')
def home():
    threads = Thread.query.all()
    return render_template('home.html', user=g.user, threads=threads)

@mod.before_request
def before_request():
    g.user = None
    if 'user_id' in session:
        g.user = User.query.get(session['user_id'])

@mod.route('/login/', methods=['GET', 'POST'])
def login():
    """
    """
    if g.user:
        return redirect(url_for('frontends.home'))
    form = LoginForm(request.form)
    # make sure data is valid, but doesn't validate password is right
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # we use werzeug to validate user's password
        if user and check_password_hash(user.password, form.password.data):
            # the session can't be modified as it's signed,
            # it's a safe place to store the user id
            session['user_id'] = user.id
            # flash('Welcome %s' % user.username)
            return redirect(url_for('frontends.home'))
        flash('Wrong email or password', 'error-message')
    return render_template("login.html", form=form)

@mod.route('/logout/', methods=['GET', 'POST'])
@requires_login
def logout():
    """
    """
    session.pop('user_id', None)
    return redirect(url_for('frontends.home'))

@mod.route('/register/', methods=['GET', 'POST'])
def register():
    """
    """
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        # create an user instance not yet stored in the database
        user = User(username=form.username.data, email=form.email.data, \
                password=generate_password_hash(form.password.data))
        # Insert the record in our database and commit it
        db.session.add(user)
        db.session.commit()

        # Log the user in, as he now has an id
        session['user_id'] = user.id

        # flash will display a message to the user
        flash('thanks for signing up!')
        # redirect user to the 'home' method of the user module.
        return redirect(url_for('frontends.home'))
    return render_template("register.html", form=form)
