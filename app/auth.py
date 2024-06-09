# auth.py

from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, g
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Agent
from .db import query_db, update_password, update_user, update_agent

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
        user = User(login, row['password'])
    else:
        user = Agent(login, row['password'], row['role'])

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    next = request.form.get('next')
    return redirect(next or url_for('main.home'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth.route('/profile')
@login_required
def profile():
    if '@' in current_user.get_id():
        row = query_db('SELECT * FROM user WHERE email = ?', [current_user.get_id()], one=True)
        return render_template('profile.html', first_name=row['name'] or '', last_name=row['surname'] or '', cin=row['cin'], address=row['address'] or '', phone=row['phone'])
    else:
        row = query_db('SELECT * FROM agent WHERE name = ?', [current_user.get_id()], one=True)
        return render_template('profile_agent.html', role=row['role'])

@auth.route('/profile', methods=['POST'])
@login_required
def update_profile():
    if '@' in current_user.get_id():
        first_name   = request.form.get('first_name')
        last_name    = request.form.get('last_name')
        cin          = request.form.get('cin')
        address      = request.form.get('address')
        phone        = request.form.get('phone')
    else:
        role         = request.form.get('role')
    old_password     = request.form.get('old_password')
    new_password     = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    if old_password == current_user.password and new_password == confirm_password and len(new_password) > 1:
        if update_password(current_user.get_id(), new_password) == 1:
            flash('Mot de passe mis à jour avec succès.')
            return redirect(url_for('main.home'))
    else:
        if '@' in current_user.get_id():
            update_user(current_user.get_id(), first_name, last_name, cin, address, phone)
        else:
            update_agent(current_user.get_id(), )
        flash('Profil mis à jour avec succès.')
    if '@' in current_user.get_id():
        return render_template('profile.html', first_name=first_name, last_name=last_name, cin=cin, address=address, phone=phone)
    else:
        return render_template('profile_agent.html', role=role)
