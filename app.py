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


@app.route('/toto')
def homepage():
    cursor = get_db().cursor()
    cursor.execute('''
                   SELECT id_maraicher id, prenom, nom
                   FROM annonce;
                   ''')
    annonces = cursor.fetchall()
    cursor.execute('''
                   SELECT id_maraicher id, prenom, nom
                   FROM maraicher;
                   ''')
    maraichers = cursor.fetchall()
    cursor.execute('''
                   SELECT id_maraicher id, prenom, nom
                   FROM maraicher;
                   ''')
    produits = cursor.fetchall()
    cursor.execute('''
                   SELECT id_maraicher id, prenom, nom
                   FROM maraicher;
                   ''')
    vente = cursor.fetchall()
    cursor.execute('''
                   SELECT id_maraicher id, prenom, nom
                   FROM maraicher;
                   ''')
    unite = cursor.fetchall()
    cursor.close()
    return render_template('layout.html', annonces=annonces, maraichers=maraichers, produits=produits, vente=vente, unite=unite)

@app.route('/annonce/edit', methods=['GET'])
def edit_etudiant():
    id = request.args.get('id')
    cursor = get_db().cursor()
    if id != None and id.isnumeric():
        indice = int(id)
        cursor.execute(''' 
                SELECT etudiant.id_etudiant AS id
                     , etudiant.nom_etudiant AS nom
                     , etudiant.groupe_etudiant_id AS groupe_id
                FROM etudiant
                WHERE id_etudiant = %s;
            ''', indice)
    mycursor2 = get_db().cursor()
    groupe_sql = ''' 
            SELECT id_groupe AS id, libelle_groupe AS name
            FROM groupe
            ORDER BY libelle_groupe;
        '''
    mycursor2.execute(groupe_sql)
    return render_template('etudiant/edit_etudiant.html', etudiant=mycursor.fetchone(), groupes=mycursor2.fetchall())

# === ANNONCE === #


# === PRODUIT === #

# === VENTE === #

# === POINT DE VENTE === #


if __name__ == '__main__':
    app.run()
