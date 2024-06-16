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
        return redirect(url_for('dossier.home'))

    return render_template('index.html')

# temporary for experiments
@main.route('/tst')
def tst():
    return render_template('index2.html')

@main.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico')

@main.route('/forms')
def forms():
    return render_template('forms.html')

@main.route('/thank-you')
def thank_you():
    return render_template('thank_you.html')

