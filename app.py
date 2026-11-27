#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Flask, request, render_template, redirect, flash, session, g
import pymysql.cursors

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = 'une cle(token) : grain de sel(any random string)'


def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host="serveurmysql.iut-bm.univ-fcomte.fr",
            user="nfaouz",
            password="secret",
            database="BDD_nfaouz",
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.route('/')
def homepage():
    return render_template('layout.html')


# === PRODUIT === #

@app.route('/produit/show')
def show_produit():
    mycursor = get_db().cursor()
    sql = '''
        SELECT produit.id_produit AS id,
               produit.nom_produit AS nom,
               produit.type_produit_id AS type_id,
               produit.saison_pousse AS saison,
               produit.prix_produit_conseille AS prix,
               type_produit.nom_type_produit AS libelle_type
        FROM produit
        INNER JOIN type_produit ON type_produit.id_type_produit = produit.type_produit_id
        ORDER BY produit.id_produit;
    '''
    mycursor.execute(sql)
    produits = mycursor.fetchall()
    return render_template('produit/show_produit.html', produits=produits)


@app.route('/produit/add')
def add_produit():
    mycursor = get_db().cursor()
    sql = '''SELECT id_type_produit AS id, nom_type_produit AS libelle
             FROM type_produit
             ORDER BY nom_type_produit;'''
    mycursor.execute(sql)
    types_produit = mycursor.fetchall()
    return render_template('produit/add_produit.html', types_produit=types_produit)


@app.route('/produit/add', methods=['POST'])
def valid_add_produit():
    nom = request.form.get('nom')
    type_id = request.form.get('type_id')
    saison = request.form.get('saison')
    prix = request.form.get('prix')

    mycursor = get_db().cursor()
    sql = '''INSERT INTO produit(id_produit, nom_produit, type_produit_id, saison_pousse, prix_produit_conseille)
             VALUES (NULL, %s, %s, %s, %s);'''
    tuple_param = (nom, type_id, saison, prix)
    mycursor.execute(sql, tuple_param)
    get_db().commit()

    flash(f'Ajout produit : nom={nom}, type_id={type_id}, saison={saison}, prix={prix}', 'alert-success')
    return redirect('/produit/show')


@app.route('/produit/delete')
def delete_produit():
    id_produit = request.args.get('id')
    mycursor = get_db().cursor()
    mycursor.execute('SELECT COUNT(*) AS nb FROM recolte WHERE produit_id = %s;', (id_produit,))
    nb_recoltes = mycursor.fetchone()['nb']

    mycursor.execute('SELECT COUNT(*) AS nb FROM annonce WHERE produit_id = %s;', (id_produit,))
    nb_annonces = mycursor.fetchone()['nb']

    if nb_recoltes > 0 or nb_annonces > 0:
        flash(f'Suppression impossible : ce produit est utilisé dans {nb_recoltes} récolte(s) et {nb_annonces} annonce(s).', 'alert-danger')
        return redirect('/produit/show')

    sql = '''DELETE FROM produit WHERE id_produit = %s;'''
    mycursor.execute(sql, (id_produit,))
    get_db().commit()

    flash(f'Suppression produit : id={id_produit}', 'alert-warning')
    return redirect('/produit/show')


@app.route('/produit/edit')
def edit_produit():
    id_produit = request.args.get('id')
    mycursor = get_db().cursor()

    sql = '''SELECT id_produit AS id,
                    nom_produit AS nom,
                    type_produit_id AS type_id,
                    saison_pousse AS saison,
                    prix_produit_conseille AS prix
             FROM produit
             WHERE id_produit = %s;'''
    mycursor.execute(sql, (id_produit,))
    produit = mycursor.fetchone()

    sql_types = '''SELECT id_type_produit AS id, nom_type_produit AS libelle
                   FROM type_produit
                   ORDER BY nom_type_produit;'''
    mycursor.execute(sql_types)
    types_produit = mycursor.fetchall()

    return render_template('produit/edit_produit.html', produit=produit, types_produit=types_produit)


@app.route('/produit/edit', methods=['POST'])
def valid_edit_produit():
    id_produit = request.form.get('id')
    nom = request.form.get('nom')
    type_id = request.form.get('type_id')
    saison = request.form.get('saison')
    prix = request.form.get('prix')

    mycursor = get_db().cursor()
    sql = '''UPDATE produit
             SET nom_produit = %s,
                 type_produit_id = %s,
                 saison_pousse = %s,
                 prix_produit_conseille = %s
             WHERE id_produit = %s;'''
    tuple_param = (nom, type_id, saison, prix, id_produit)
    mycursor.execute(sql, tuple_param)
    get_db().commit()

    flash(f'Modification produit : id={id_produit}, nom={nom}, type_id={type_id}, saison={saison}, prix={prix}', 'alert-success')
    return redirect('/produit/show')


@app.route('/produit/etat')
def etat_produit():
    mycursor = get_db().cursor()

    saison_choisie = request.args.get('saison', '')
    type_id_choisi = request.args.get('type_id', '')

    sql_types = '''SELECT id_type_produit AS id, nom_type_produit AS libelle
                   FROM type_produit
                   ORDER BY nom_type_produit;'''
    mycursor.execute(sql_types)
    types_produit = mycursor.fetchall()

    # 1. Nombre de produits par saison selon la sélection (saison et/ou type)
    sql_stats = '''
        SELECT produit.saison_pousse AS saison,
               COUNT(produit.id_produit) AS nb_produits
        FROM produit
        INNER JOIN type_produit ON type_produit.id_type_produit = produit.type_produit_id
        WHERE (%s = '' OR produit.saison_pousse = %s)
          AND (%s = '' OR produit.type_produit_id = %s)
        GROUP BY produit.saison_pousse
        ORDER BY produit.saison_pousse;
    '''
    mycursor.execute(sql_stats, (saison_choisie, saison_choisie, type_id_choisi, type_id_choisi))
    stats_saisons = mycursor.fetchall()

    # 2. Produits concernés par la sélection
    sql_produits = '''
        SELECT produit.id_produit AS id,
               produit.nom_produit AS nom,
               produit.type_produit_id AS type_id,
               type_produit.nom_type_produit AS libelle_type,
               produit.saison_pousse AS saison,
               produit.prix_produit_conseille AS prix
        FROM produit
        INNER JOIN type_produit ON type_produit.id_type_produit = produit.type_produit_id
        WHERE (%s = '' OR produit.saison_pousse = %s)
          AND (%s = '' OR produit.type_produit_id = %s)
        ORDER BY produit.nom_produit;
    '''
    mycursor.execute(sql_produits, (saison_choisie, saison_choisie, type_id_choisi, type_id_choisi))
    produits_concernes = mycursor.fetchall()

    return render_template('produit/etat_produit.html',
                           stats_saisons=stats_saisons,
                           produits_concernes=produits_concernes,
                           types_produit=types_produit,
                           saison_choisie=saison_choisie,
                           type_id_choisi=type_id_choisi)


if __name__ == '__main__':
    app.run(debug=True)