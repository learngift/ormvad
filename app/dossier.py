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
from werkzeug.utils import secure_filename

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

@dossier.route('/edit_request/<int:demande_id>', methods=['GET', 'POST'])
@login_required
def edit_request(demande_id):
    if request.method == 'POST':
        # Logique pour éditer la demande d'examen
        name = request.form.get('name')
        surname = request.form.get('surname')
        raison_sociale = request.form.get('raison_sociale')
        cin = request.form.get('cin')
        douar = request.form.get('douar')
        commune_rurale = request.form.get('commune_rurale')
        cercle = request.form.get('cercle')
        province = request.form.get('province')
        address = request.form.get('address')
        phone = request.form.get('phone')
        objet = request.form.get('objet')
        superficie = request.form.get('superficie')
        effectif = request.form.get('effectif')

        db = get_db()
        db.execute(
            'UPDATE dmd_exam_cons_elevage SET name = ?, surname = ?, raison_sociale = ?, cin = ?, douar = ?, commune_rurale = ?, cercle = ?, province = ?, address = ?, phone = ?, objet = ?, superficie = ?, effectif = ? WHERE id = ?',
            (name, surname, raison_sociale, cin, douar, commune_rurale, cercle, province, address, phone, objet, superficie, effectif, demande_id)
        )
        db.commit()

        flash('Dossier mis à jour avec succès.')
        return redirect(url_for('dossier.edit_request', demande_id=demande_id))
    
    row = query_db('SELECT * FROM demande JOIN dmd_exam_cons_elevage ON demande.id = dmd_exam_cons_elevage.id WHERE demande.id = ?',
                   [demande_id], one=True)
    pieces = query_db('SELECT * FROM piece WHERE dmd_id = ?', [demande_id])
    return render_template('dossier_ex.html', d=row, pieces=pieces)



@dossier.route('/delete_request/<int:demande_id>', methods=['POST'])
@login_required
def delete_request(demande_id):
    # Logique pour supprimer la demande d'examen
    db = get_db()
    db.execute('DELETE FROM demande WHERE id = ? AND email = ?', [ demande_id, current_user.get_id() ] )
    db.execute('DELETE FROM dmd_exam_cons_elevage WHERE id = ? ', [ demande_id ])
    db.execute('DELETE FROM piece WHERE dmd_id = ?', [ demande_id ] )
    db.commit()

    flash('Dossier supprimé avec succès.')
    return redirect(url_for('dossier.home'))

@dossier.route('/valid_request/<int:demande_id>', methods=['POST'])
@login_required
def valid_request(demande_id):
    # Logique pour valider la demande d'examen
    db = get_db()
    db.execute("UPDATE demande SET etat='complet' WHERE id = ? AND email = ?", [ demande_id, current_user.get_id() ] )
    db.commit()

    flash('Dossier envoyé avec succès pour l\'analyse par le guichet unique.')
    return redirect(url_for('main.thank_you'))


@dossier.route('/upload_document/<int:demande_id>', methods=['POST'])
@login_required
def upload_document(demande_id):
    orig = url_for('dossier.edit_request', demande_id=demande_id)
    if 'file' not in request.files:
        flash('No file part')
        return redirect(orig)
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(orig)
    if file:
        filename = secure_filename(file.filename)
        user_folder = os.path.join('data', current_user.get_id(), str(demande_id))
        print('upload ' + user_folder)
        os.makedirs(user_folder, exist_ok=True)
        file_path = os.path.join(user_folder, filename)
        file.save(file_path)
        print('upload ' + file_path)
        flash('File successfully uploaded')
        print('upload success')
        db = get_db()
        db.execute("INSERT INTO piece (dmd_id, date_piece, filename) VALUES ( ?, datetime('now'), ? )", [ demande_id, filename ])
        db.commit()

        return redirect(orig)

@dossier.route('/piece/<int:demande_id>/<id>')
def afficher_piece(demande_id, id):
    row = query_db('SELECT filename FROM piece WHERE id = ? ', [id], one=True)
    print('afficher_piece for id ' + str(id) + ' ' + row[0])
    print('data/' + current_user.get_id() + '/' + str(demande_id))
    return send_from_directory('../data/' + current_user.get_id() + '/' + str(demande_id), row[0])

@dossier.route('/delete_piece/<int:demande_id>/<piece_id>', methods=['POST'])
def delete_piece(demande_id, piece_id):
    orig = url_for('dossier.edit_request', demande_id=demande_id)
    db = get_db()
    db.execute('DELETE FROM piece WHERE id = ?', [ piece_id ] )
    db.commit()
    flash('Pièce supprimée')
    return redirect(orig)
