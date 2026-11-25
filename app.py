import datetime

from flask import Flask, request, render_template, redirect, flash

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = 'une cle(token) : grain de sel(any random string)'

from flask import session, g
import pymysql.cursors


def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            #host="127.0.0.1", # Utilisé si python tourne en local
            host="miambiodb", # Utilisé quand python tourne dans un container docker
            port=3306,
            user="miambio",
            password="getmemycarrots",
            database="miambio",
            charset='utf8mb4',  # 2 attributs à ajouter
            cursorclass=pymysql.cursors.DictCursor  # 2 attributs à ajouter
        )
    return g.db


@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


# === ANNONCE === #

# maraicher_id    BIGINT,
# produit_id      INT,
# vente_id        INT,
# unite_id        TINYINT,
# prix_produit    SMALLINT,
# quantite_vendue SMALLINT,
# PRIMARY KEY (maraicher_id, produit_id, vente_id, unite_id),
# FOREIGN KEY (maraicher_id) REFERENCES maraicher (id_maraicher),
# FOREIGN KEY (produit_id) REFERENCES produit (id_produit),
# FOREIGN KEY (vente_id) REFERENCES vente (id_vente),
# FOREIGN KEY (unite_id) REFERENCES unite (id_unite)

@app.route('/')
def homepage():
    maraicherCursor = get_db().cursor()
    maraicherCursor.execute('''
        SELECT id_maraicher AS id, prenom, nom
        FROM maraicher;
    ''')
    return render_template('layout.html')

# === PRODUIT === #

@app.route('/')
@app.route('/produit/show')
def show_produit():
    mycursor = get_db().cursor()
    sql = '''
        SELECT produit.id_produit AS id,
               produit.nom_produit AS nom,
               produit.type_produit_id AS type_id,
               produit.saison_pousse AS saison,
               produit.prix_produit_conseille AS prix,
               type_produit.libelle_type_produit AS libelle_type
        FROM produit
        INNER JOIN type_produit ON type_produit.id_type_produit = produit.type_produit_id
        ORDER BY produit.nom_produit;
    '''
    mycursor.execute(sql)
    produits = mycursor.fetchall()
    return render_template('produit/show_produit.html', produits=produits)


@app.route('/produit/add')
def add_produit():
    mycursor = get_db().cursor()
    sql = '''SELECT id_type_produit AS id, libelle_type_produit AS libelle
             FROM type_produit
             ORDER BY libelle_type_produit;'''
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
    sql = '''DELETE FROM produit WHERE id_produit = %s;'''
    tuple_param = (id_produit,)
    mycursor.execute(sql, tuple_param)
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

    sql_types = '''SELECT id_type_produit AS id, libelle_type_produit AS libelle
                   FROM type_produit
                   ORDER BY libelle_type_produit;'''
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

    # Récupération des paramètres de filtrage (GET)
    saison_choisie = request.args.get('saison', '')
    type_id_choisi = request.args.get('type_id', '')

    # Liste des types de produit pour la liste déroulante
    sql_types = '''SELECT id_type_produit AS id, libelle_type_produit AS libelle
                   FROM type_produit
                   ORDER BY libelle_type_produit;'''
    mycursor.execute(sql_types)
    types_produit = mycursor.fetchall()

    # 1. Nombre de produits par saison (sans if/else grâce au OR)
    sql_saison = '''
        SELECT produit.saison_pousse AS saison,
               COUNT(produit.id_produit) AS nb_produits
        FROM produit
        INNER JOIN type_produit ON type_produit.id_type_produit = produit.type_produit_id
        WHERE (%s = '' OR produit.saison_pousse = %s)
        GROUP BY produit.saison_pousse
        ORDER BY produit.saison_pousse;
    '''
    mycursor.execute(sql_saison, (saison_choisie, saison_choisie))
    stats_saisons = mycursor.fetchall()

    # 2. Prix moyen par type de produit (sans if/else grâce au OR)
    sql_prix = '''
        SELECT type_produit.id_type_produit AS id,
               type_produit.libelle_type_produit AS libelle,
               COUNT(produit.id_produit) AS nb_produits,
               ROUND(AVG(produit.prix_produit_conseille), 2) AS prix_moyen
        FROM type_produit
        LEFT JOIN produit ON produit.type_produit_id = type_produit.id_type_produit
        WHERE (%s = '' OR type_produit.id_type_produit = %s)
        GROUP BY type_produit.id_type_produit, type_produit.libelle_type_produit
        ORDER BY type_produit.libelle_type_produit;
    '''
    mycursor.execute(sql_prix, (type_id_choisi, type_id_choisi))
    stats_prix = mycursor.fetchall()

    return render_template('produit/etat_produit.html',
                           stats_saisons=stats_saisons,
                           stats_prix=stats_prix,
                           types_produit=types_produit,
                           saison_choisie=saison_choisie,
                           type_id_choisi=type_id_choisi)



# === VENTE === #

# === POINT DE VENTE === #


if __name__ == '__main__':
    app.run()
