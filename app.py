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
            # host="127.0.0.1", # Utilisé si python tourne en local
            host="miambiodb",  # Utilisé quand python tourne dans un container docker
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

@app.route('/annonces/show')
def show_annonce():
    cursor = get_db().cursor()
    cursor.execute('''
                   SELECT a.*, p.nom_produit
                   FROM annonce a
                   JOIN produit p ON p.id_produit = a.produit_id;
                   ''')
    annonces = cursor.fetchall()
    cursor.close()
    return render_template('annonce/show_annonce.html', annonces=annonces)

@app.route('/annonce/edit', methods=['GET'])
def edit_annonce():
    idMaraicher = request.args.get('maraicher')
    idVente = request.args.get('vente')
    idProduit = request.args.get('produit')
    idUnite = request.args.get('unite')
    cursor = get_db().cursor()
    if idMaraicher != None and idMaraicher.isnumeric() and idVente != None and idMaraicher.isnumeric() and idProduit != None and idProduit.isnumeric() and idUnite != None and idUnite.isnumeric():
        cursor.execute(''' 
                SELECT *
                FROM annonce
                WHERE maraicher_id = %s AND vente_id = %s AND produit_id = %s AND unite_id = %s;
            ''', (idMaraicher, idVente, idProduit, idUnite))
    annonce = cursor.fetchone()
    cursor.execute(''' 
            SELECT id_maraicher, raison_sociale
            FROM maraicher
            ORDER BY raison_sociale;
        ''')
    maraichers = cursor.fetchall()
    cursor.execute('''
                   SELECT id_produit, nom_produit
                   FROM produit
                   ORDER BY nom_produit;
                   ''')
    produits = cursor.fetchall()
    cursor.execute('''
                   SELECT id_vente, pdv.nom_point_de_vente, vente.date_vente
                   FROM vente
                    JOIN point_de_vente pdv ON pdv.id_point_de_vente = vente.point_de_vente_id;
                   ''')
    ventes = cursor.fetchall()
    cursor.execute('''
                   SELECT id_unite, nom_unite
                   FROM unite
                   ORDER BY nom_unite;
                   ''')
    unites = cursor.fetchall()
    return render_template('annonce/edit_annonce.html', annonce=annonce, maraichers=maraichers, produits=produits, ventes=ventes, unites=unites)

@app.route('/annonce/edit', methods=['POST'])
def valid_edit_annonce():
    maraicher_id = request.form.get('maraicher_id')
    produit_id = request.form.get('produit_id'),
    vente_id = request.form.get('vente_id'),
    unite_id = request.form.get('unite_id')
    prix_produit = request.form.get('prix_produit')
    quantite_vendue = request.form.get('quantite_vendue')
    cursor = get_db().cursor()
    cursor.execute('''UPDATE annonce SET prix_produit = %s, quantite_vendue = %s WHERE maraicher_id=%s AND produit_id = %s AND vente_id = %s AND unite_id = %s ''',(prix_produit, quantite_vendue, maraicher_id, produit_id, vente_id, unite_id))
    get_db().commit()
    return redirect('/annonces/show')

@app.route('/annonce/add', methods=['GET'])
def add_annonce():
    cursor = get_db().cursor()
    cursor.execute(''' 
            SELECT id_maraicher, raison_sociale
            FROM maraicher
            ORDER BY raison_sociale;
        ''')
    maraichers = cursor.fetchall()
    cursor.execute('''
                   SELECT id_produit, nom_produit
                   FROM produit
                   ORDER BY nom_produit;
                   ''')
    produits = cursor.fetchall()
    cursor.execute('''
                   SELECT id_vente, pdv.nom_point_de_vente, vente.date_vente
                   FROM vente
                    JOIN point_de_vente pdv ON pdv.id_point_de_vente = vente.point_de_vente_id;
                   ''')
    ventes = cursor.fetchall()
    cursor.execute('''
                   SELECT id_unite, nom_unite
                   FROM unite
                   ORDER BY nom_unite;
                   ''')
    unites = cursor.fetchall()
    return render_template('annonce/add_annonce.html', maraichers=maraichers, produits=produits, ventes=ventes, unites=unites)

@app.route('/annonce/add', methods=['POST'])
def valid_add_annonce():
    maraicher_id = request.form.get('maraicher_id')
    produit_id = request.form.get('produit_id'),
    vente_id = request.form.get('vente_id'),
    unite_id = request.form.get('unite_id')
    prix_produit = request.form.get('prix_produit')
    quantite_vendue = request.form.get('quantite_vendue')
    cursor = get_db().cursor()
    cursor.execute('''INSERT INTO annonce(maraicher_id, produit_id, vente_id, unite_id, prix_produit, quantite_vendue) VALUES(%s,%s,%s,%s,%s,%s) ''',(maraicher_id, produit_id, vente_id, unite_id, prix_produit, quantite_vendue))
    get_db().commit()
    return redirect('/annonces/show')

@app.route('/annonce/delete', methods=['GET'])
def delete_annonce():
    idMaraicher = request.args.get('maraicher')
    idVente = request.args.get('vente')
    idProduit = request.args.get('produit')
    idUnite = request.args.get('unite')
    if idMaraicher != None and idMaraicher.isnumeric() and idVente != None and idMaraicher.isnumeric() and idProduit != None and idProduit.isnumeric() and idUnite != None and idUnite.isnumeric():
        cursor = get_db().cursor()
        cursor.execute('''
                       DELETE
                       FROM annonce
                       WHERE maraicher_id = %s
                         AND vente_id = %s
                         AND produit_id = %s
                         AND unite_id = %s;
                       ''', (idMaraicher, idVente, idProduit, idUnite))
        get_db().commit()
    return redirect('/annonces/show')

# === ANNONCE === #


# === PRODUIT === #

# === VENTE === #

# === POINT DE VENTE === #


if __name__ == '__main__':
    app.run()
