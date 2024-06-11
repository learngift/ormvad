# __init__.py
# tutorial from https://github.com/PrettyPrinted/flask_auth_scotch

from flask_bootstrap import Bootstrap5
from flask import Flask, g
from flask_mail import Mail
from flask_login import LoginManager 

from .site_config import secret_key, database_name, mail_account
import logging
import datetime
from .db import query_db

def format_time(date_iso):
    return datetime.datetime.fromisoformat(date_iso).strftime("%d/%m/%Y")

def create_app():

    logging.basicConfig(filename='record.log', level=logging.DEBUG)

    app = Flask(__name__)

    app.logger.setLevel("INFO")
    app.logger.info('Démarrage du site')

    app.secret_key = secret_key

    app.config['DATABASE']             = database_name
    
    # Parameters used by Flask-Mail
    app.config['MAIL_SERVER']   = '127.0.0.1'
    app.config['MAIL_PORT']     = 25
    app.config['MAIL_USERNAME'] = mail_account
    app.config['MAIL_PASSWORD'] = ''
    app.config['MAIL_USE_TLS']  = False
    app.config['MAIL_USE_SSL']  = False

    from . import db
    db.init_app(app)

    app.config['BOOTSTRAP_SERVE_LOCAL'] = True
    bootstrap = Bootstrap5(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page'
    login_manager.init_app(app)

    from .models import User, Agent

    @login_manager.user_loader
    def load_user(user_id):
        if '@' in user_id:
            user_row = query_db('SELECT * FROM user WHERE email = ?', [user_id], one=True)
            if user_row:
                return User(user_id, user_row['password'])
        else:
            agent_row = query_db('SELECT * FROM agent WHERE name = ?', [user_id], one=True)
            if agent_row:
                return Agent(user_id, agent_row['password'], agent_row['role'])
        return None

    # blueprint for auth routes in our app
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for main parts of app
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # blueprint for parts of app concerning dossiers
    from .dossier import dossier as dossier_blueprint
    app.register_blueprint(dossier_blueprint)

    # blueprint for admin parts of app
    #from .admin import admin as admin_blueprint
    #app.register_blueprint(admin_blueprint)

    app.jinja_env.globals.update(format_time=format_time)

    return app
