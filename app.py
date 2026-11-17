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
            host="localhost",  # localhost sur les machines perso.
            user="damien",
            password="password",
            database="etudiant",
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
def show_etudiants():
    return render_template('layout.html')

@app.route('/annonces', methods=['GET'])
def add_annonce():
    mycursor = get_db().cursor()
    sql = '''
          SELECT *
          FROM groupe;
          '''
    mycursor.execute(sql)
    return render_template('etudiant/add_etudiant.html', groupes=mycursor.fetchall())

@app.route('/annonce/add', methods=['GET'])
def add_annonce():
    maraicherCursor = get_db().cursor()
    maraicherCursor.execute('''
        SELECT id_maraicher AS id, libelle_maraicher AS name
        FROM maraicher;
    ''')
    maraicherCursor = get_db().cursor()
    maraicherCursor.execute('''
        SELECT id_maraicher AS id, libelle_maraicher AS name
        FROM produit;
    ''')
    maraicherCursor = get_db().cursor()
    maraicherCursor.execute('''
        SELECT id_maraicher AS id, libelle_maraicher AS name
        FROM vente;
    ''')
    maraicherCursor = get_db().cursor()
    maraicherCursor.execute('''
        SELECT id_maraicher AS id, libelle_maraicher AS name
        FROM vente;
    ''')
    return render_template(
        'etudiant/add_etudiant.html',
        maraichers=maraicherCursor.fetchall()
    )

@app.route('/annonce/delete')
def delete_etudiant():
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql = '''
          DELETE
          FROM etudiant
          WHERE id_etudiant = %s; \
          '''
    mycursor.execute(sql, (id))
    get_db().commit()
    message = 'Suppression de l\'étudiant d\'identifiant :' + str(id)
    flash(message, 'is-danger')
    return redirect('/')


@app.route('/annonce/edit', methods=['GET'])
def edit_etudiant():
    id = request.args.get('id')
    mycursor = get_db().cursor()
    if id != None and id.isnumeric():
        indice = int(id)
        sql = '''
              SELECT etudiant.id_etudiant        AS id
                   , etudiant.nom_etudiant       AS nom
                   , etudiant.groupe_etudiant_id AS groupe_id
              FROM etudiant
              WHERE id_etudiant = %s; \
              '''
        mycursor.execute(sql, (indice))
    mycursor2 = get_db().cursor()
    groupe_sql = '''
                 SELECT id_groupe AS id, libelle_groupe AS name
                 FROM groupe
                 ORDER BY libelle_groupe; \
                 '''
    mycursor2.execute(groupe_sql)
    return render_template('etudiant/edit_etudiant.html', etudiant=mycursor.fetchone(), groupes=mycursor2.fetchall())


@app.route('/annonce/add', methods=['POST'])
def valid_add_etudiant():
    nom = request.form.get('nom', 'None nom')
    id_groupe = request.form.get('id_groupe', 'None id_groupe')
    message = 'Ajout d\'un étudiant de nom :' + str(nom) + ' - id_groupe :' + str(id_groupe)
    flash(message, 'is-success')
    mycursor = get_db().cursor()
    sql = '''
          INSERT
          INTO etudiant(id_etudiant, nom_etudiant, groupe_etudiant_id)
          VALUES (NULL, %s, %s); \
          '''
    mycursor.execute(sql, (nom, id_groupe))
    get_db().commit()
    return redirect('/')


@app.route('/annonce/edit', methods=['POST'])
def valid_edit_etudiant():
    id = request.form.get('id', 'None id')
    nom = request.form.get('nom', 'None nom')
    id_groupe = request.form.get('id_groupe', 'None id_groupe')
    message = 'Modification du nom :' + str(nom) + ' - id_groupe :' + str(
        id_groupe) + ' pour l\'étudiant d\'identifiant :' + str(id)
    flash(message, 'is-success')
    mycursor = get_db().cursor()
    sql = '''
          UPDATE etudiant
          SET nom_etudiant       = %s,
              groupe_etudiant_id = %s
          WHERE id_etudiant = %s; \
          '''
    mycursor.execute(sql, (nom, id_groupe, id))
    get_db().commit()
    return redirect('/')


# === PRODUIT === #

# === VENTE === #

# === POINT DE VENTE === #


if __name__ == '__main__':
    app.run()
