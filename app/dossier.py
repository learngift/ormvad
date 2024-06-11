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

dossier = Blueprint('dossier', __name__)

@dossier.route('/home')
@login_required
def home():
    if isinstance(current_user, User):
        demandes = query_db('SELECT * FROM demande WHERE email = ?', [current_user.get_id()])
        return render_template('home.html', demandes=demandes)
    else:
        demandes = query_db('SELECT * FROM demande')
        return render_template('home_agent.html', demandes=demandes)

@dossier.route('/create_request')
@login_required
def create_request():
    user_row = query_db('SELECT * FROM user WHERE email = ?', [current_user.get_id()], one=True)

    query_db("INSERT INTO demande (email, date_demande, designation, etat) VALUES (?, datetime('now'), 'construction batiment élevage', 'En cours')",
             [current_user.get_id()])
    
    # Récupérer l'ID de la demande nouvellement créée
    demande_id = query_db('SELECT last_insert_rowid() AS id', one=True)['id']
    
    # Insérer les détails de la demande spécifique dans la table `dmd_exam_cons_elevage`
    query_db('INSERT INTO dmd_exam_cons_elevage (id, name, surname, cin, address, phone) VALUES (?, ?, ?, ?, ?, ?)',
             [demande_id, user_row['name'], user_row['surname'], user_row['cin'], user_row['address'], user_row['phone']])
    
    # Récupérer la demande nouvellement créée pour l'afficher
    row = query_db('SELECT * FROM demande JOIN dmd_exam_cons_elevage ON demande.id = dmd_exam_cons_elevage.id WHERE demande.id = ?',
                   [demande_id], one=True)
    return render_template('dossier_ex.html', d=row)

@dossier.route('/edit_request/<int:demande_id>')
@login_required
def edit_request(demande_id):
    row = query_db('SELECT * FROM demande JOIN dmd_exam_cons_elevage ON demande.id = dmd_exam_cons_elevage.id WHERE demande.id = ?',
                   [demande_id], one=True)
    return render_template('dossier_ex.html', d=row)

@dossier.route('/delete_request/<int:demande_id>', methods=['POST'])
@login_required
def delete_request(demande_id):
    # Logique pour supprimer la demande d'examen
    db = get_db()
    db.execute('DELETE FROM demande WHERE id = ? AND email = ?', [ demande_id, current_user.get_id() ] )
    db.execute('DELETE FROM dmd_exam_cons_elevage WHERE id = ? ', [ demande_id ])
    db.commit()

    flash('Dossier supprimé avec succès.')
    return redirect(url_for('dossier.home'))