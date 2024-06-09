# main.py

from flask import Blueprint, render_template, send_from_directory, current_app, request, flash, Response, redirect, url_for, abort, send_file
from flask_login import login_required, current_user
import os, sys
import mimetypes
import subprocess
import urllib.parse
import datetime
from .db import get_db, query_db
from .models import User

main = Blueprint('main', __name__)

@main.context_processor
def inject_len():
    return dict(len=len)

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    return render_template('index.html')

# temporary for experiments
@main.route('/tst')
def tst():
    return render_template('index2.html')

@main.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

@main.route('/home')
@login_required
def home():
    if isinstance(current_user, User):
        demandes = query_db('SELECT * FROM demande WHERE email = ?', [current_user.get_id()])
        return render_template('home.html', demandes=demandes)
    else:
        demandes = query_db('SELECT * FROM demande')
        return render_template('home_agent.html', demandes=demandes)


# TODO
@main.route('/create_request')
@login_required
def create_request():
    return redirect(url_for('main.home'))

# TODO
@main.route('/edit_request/<int:demande_id>')
@login_required
def edit_request(demande_id):
    return redirect(url_for('main.home'))

@main.route('/forms')
def forms():
    return render_template('forms.html')

@main.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Récupérez les données du formulaire
        form_data = request.form
        # Traitez les données du formulaire (par exemple, enregistrez-les dans une base de données)
        # ...
        return redirect(url_for('main.thank_you'))
    return render_template('form.html')

@main.route('/thank-you')
def thank_you():
    return "Thank you for submitting the form!"

