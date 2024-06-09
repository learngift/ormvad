# auth.py

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, g
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Agent
from .db import query_db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    remember = bool(request.form.get('remember'))

    login    = request.form.get('login')
    password = request.form.get('password')
    user     = None

    if '@' in login :
        row = query_db('SELECT * FROM user WHERE email = ?', [login], one=True)
    else:
        row = query_db('SELECT * FROM agent WHERE name = ?', [login], one=True)
    if row == None:
        flash('Unknown login. Please check your details and try again.')
        return redirect(url_for('auth.login'))
    if password != row['password']:
        flash('Wrong password. Please check your details and try again.')
        return redirect(url_for('auth.login'))

    if '@' in login :
        user = User(row['username'], row['password'])
    else:
        user = Agent(row['name'], row['password'], row['role'])

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    next = request.form.get('next')
    return redirect(url_for('main.home') if next == None else next)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
