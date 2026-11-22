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
            host="127.0.0.1", # Utilisé si python tourne en local
            #host="miambiodb", # Utilisé quand python tourne dans un container docker
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

# === VENTE === #

# === POINT DE VENTE === #


if __name__ == '__main__':
    app.run()
