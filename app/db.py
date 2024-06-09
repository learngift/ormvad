# db.py
import csv
import datetime
import os
import sqlite3

import click
from flask import Flask, current_app, g
from flask.cli import with_appcontext
from collections import defaultdict

# #############################################################
# helper classes (like records)

# #############################################################
# boilerplate
def get_db():
    if 'db' not in g:
        # print(f"trying to open {current_app.config['DATABASE']}")
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    try:
        rv = cur.fetchall()
    finally:
        cur.close()
    get_db().commit()
    # print ('len of result is ' + str(len(rv) if rv else -1))
    return (rv[0] if rv else None) if one else rv

# #############################################################
# db services
def update_password(id, password):
    if '@' in id:
        cursor = get_db().execute('UPDATE user SET password = ? WHERE email = ?', [password, id ])
    else:
        cursor = get_db().execute('UPDATE agent SET password = ? WHERE name = ?', [password, id])
    get_db().commit()
    return cursor.rowcount

def update_user(id, first_name, last_name, cin, address, phone):
    get_db().execute('UPDATE user SET name = ?, surname = ?, cin = ?, address = ?, phone = ? WHERE email = ?', [first_name, last_name, cin, address, phone, id])
    get_db().commit()

def update_agent(id, role):
    get_db().execute('UPDATE agent SET role = ? WHERE name = ?', [role, id])
    get_db().commit()




# #############################################################
# command line utilities
# This function initializes the database by clearing existing data and creating new tables.
# It uses the 'click' library to create a command-line interface.
# The 'with_appcontext' decorator ensures that the function runs within the application context.
@click.command('init-db')
@with_appcontext
def click_init_db_command():
    """Clear the existing data and create new tables."""
    with current_app.open_resource('schema.sql') as f:
        get_db().executescript(f.read().decode('utf8'))
    click.echo('Initialized the database.')

# This function dumps the content of a table into a CSV file.
# It takes the filename, headers, and query result as parameters.
# The function writes the headers and each row of the query result into the CSV file.
def generic_dump_table(filename, headers, query_result):
    """Dump the content of a table into a csv file"""
    with open(filename, 'w') as f1:
        writer = csv.writer(f1, delimiter=';')
        writer.writerow(headers)
        for row in query_result:
            writer.writerow([row[h] for h in headers])

# This function imports the content of a file into a table.
# It takes the input file, headers, and table name as parameters.
# The function reads the file, checks the headers, and inserts each row into the table.
def generic_import_table(input, headers, table):
    """Imp the content of file into table """
    reader = csv.reader(input, delimiter=';')
    file_headers = next(reader)
    if file_headers != headers:
        raise click.ClickException('wrong header content, it shall be ' + ';'.join(headers))
    cur = get_db().cursor()
    cur.execute(f"DELETE FROM {table}")
    get_db().commit()
    cur.execute('BEGIN TRANSACTION')
    insert_cmd = f"INSERT INTO {table} ({', '.join(headers)}) values ({', '.join(['?' for h in headers])})"
    for row in reader:
        cur.execute(insert_cmd, row)
        print('row ' + row[0] + ' loaded')
    get_db().commit()
    click.echo(f"Table {table} loaded.")



@click.command('dump-db')
@with_appcontext
def click_dump_db_command():
    """Dump the content of database into csv files"""
    get_db() # open the database before changing directory
    timestamp = datetime.datetime.now().strftime('%Y%m%d')
    i = 0
    dirname = f"dump_db_{timestamp}"
    while os.path.isdir(dirname):
        i = i+1
        dirname = f"dump_db_{timestamp}_{i}"
    os.mkdir(dirname)
    os.chdir(dirname)
    generic_dump_table('db_user.csv',
                       ['email', 'password'],
                       query_db('SELECT * FROM user'))

    generic_dump_table('db_agent.csv',
                       ['name', 'password', 'role'],
                       query_db('SELECT * FROM agent'))

    click.echo('Database dumped.')

@click.command('imp-user-db')
@click.argument('input', type=click.File('r'))
@with_appcontext
def click_imp_user_db_command(input):
    """Imp csv file into table user"""
    generic_import_table(input, ['email', 'password'], 'user')

@click.command('imp-agent-db')
@click.argument('input', type=click.File('r'))
@with_appcontext
def click_imp_agent_db_command(input):
    """Imp csv file into table delivery_report"""
    generic_import_table(input, ['name', 'password', 'role'], 'agent')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(click_init_db_command)
    app.cli.add_command(click_dump_db_command)
    app.cli.add_command(click_imp_user_db_command)
    app.cli.add_command(click_imp_agent_db_command)
