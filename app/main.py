# main.py

from flask import Blueprint, render_template, send_from_directory, current_app, request, flash, Response, redirect, url_for, abort, send_file
from flask_login import login_required, current_user
import os, sys
import mimetypes
import subprocess
import urllib.parse
import datetime
from .db import get_db

main = Blueprint('main', __name__)

@main.context_processor
def inject_len():
    return dict(len=len)

@main.route('/')
def index():
    return render_template('index.html')
    # return redirect(url_for('auth.login'))

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
    return render_template('home.html')

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

