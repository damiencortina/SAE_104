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

@app.route('/point_de_vente/show')
def show_point_de_vente():
    cursor = get_db().cursor()
    cursor.execute('''
                   SELECT point_de_vente.*,
                          ville.nom_ville
                   FROM point_de_vente
                            JOIN ville ON ville.id_ville = point_de_vente.ville_id;
                   ''')
    points_de_vente = cursor.fetchall()
    cursor.close()
    return render_template('point_de_vente/show_point_de_vente.html', points_de_vente=points_de_vente)


@app.route('/point_de_vente/add', methods=['GET'])
def add_point_de_vente():
    cursor = get_db().cursor()
    cursor.execute("""
                   SELECT id_ville, nom_ville
                   FROM ville
                   ORDER BY nom_ville;
                   """)
    villes = cursor.fetchall()
    cursor.close()
    return render_template('point_de_vente/add_point_de_vente.html', villes=villes)


@app.route('/point_de_vente/valide_add', methods=['POST'])
def valide_add_point_de_vente():
    nom = request.form.get('nom_point_de_vente')
    adresse = request.form.get('adresse_point_de_vente')
    code_postal = request.form.get('code_postal_point_de_vente')
    ville_id = request.form.get('ville_id')
    tarifs_location = request.form.get('tarifs_location')

    cursor = get_db().cursor()
    cursor.execute("""
                   INSERT INTO point_de_vente (nom_point_de_vente, adresse_point_de_vente, code_postal_point_de_vente,
                                               ville_id, tarifs_location)
                   VALUES (%s, %s, %s, %s, %s);
                   """, (nom, adresse, code_postal, ville_id, tarifs_location))
    get_db().commit()
    cursor.close()
    return redirect(url_for('show_point_de_vente'))


@app.route('/point_de_vente/edit', methods=['GET'])
def edit_point_de_vente():
    id_point = request.args.get('id')
    cursor = get_db().cursor()

    point_de_vente = None
    if id_point is not None and id_point.isnumeric():
        indice = int(id_point)
        cursor.execute("""
                       SELECT id_point_de_vente,
                              nom_point_de_vente,
                              adresse_point_de_vente,
                              code_postal_point_de_vente,
                              ville_id,
                              tarifs_location
                       FROM point_de_vente
                       WHERE id_point_de_vente = %s;
                       """, (indice,))
        point_de_vente = cursor.fetchone()

    cursor.execute("SELECT id_ville, nom_ville FROM ville ORDER BY nom_ville;")
    villes = cursor.fetchall()
    cursor.close()

    return render_template('point_de_vente/edit_point_de_vente.html',
                           point_de_vente=point_de_vente,
                           villes=villes)


@app.route('/point_de_vente/valide_edit', methods=['POST'])
def valide_edit_point_de_vente():
    id_point = request.args.get('id')
    nom = request.form.get('nom_point_de_vente')
    adresse = request.form.get('adresse_point_de_vente')
    code_postal = request.form.get('code_postal_point_de_vente')
    ville_id = request.form.get('ville_id')
    tarifs_location = request.form.get('tarifs_location')

    cursor = get_db().cursor()
    cursor.execute("""
                   UPDATE point_de_vente
                   SET nom_point_de_vente         = %s,
                       adresse_point_de_vente     = %s,
                       code_postal_point_de_vente = %s,
                       ville_id                   = %s,
                       tarifs_location            = %s
                   WHERE id_point_de_vente = %s;
                   """, (nom, adresse, code_postal, ville_id, tarifs_location, id_point))
    get_db().commit()
    cursor.close()
    return redirect(url_for('show_point_de_vente'))


@app.route('/point_de_vente/delete')
def delete_point_de_vente():
    id_point = request.args.get('id')
    if id_point is not None and id_point.isnumeric():
        cursor = get_db().cursor()

        # Nettoyage des tables dépendantes pour éviter l'IntegrityError
        cursor.execute("""
                       DELETE
                       FROM annonce
                       WHERE vente_id IN (SELECT id_vente FROM vente WHERE point_de_vente_id = %s);
                       """, (int(id_point),))

        cursor.execute("""
                       DELETE
                       FROM vente
                       WHERE point_de_vente_id = %s;
                       """, (int(id_point),))

        cursor.execute("""
                       DELETE
                       FROM point_de_vente
                       WHERE id_point_de_vente = %s;
                       """, (int(id_point),))

        get_db().commit()
        cursor.close()
    return redirect(url_for('show_point_de_vente'))


@app.route('/point_de_vente/etat')
def etat_point_de_vente():
    cursor = get_db().cursor()
    cursor.execute('''
        SELECT point_de_vente.id_point_de_vente, 
               point_de_vente.nom_point_de_vente, 
               COUNT(vente.id_vente) AS nombre_de_ventes
        FROM point_de_vente
        LEFT JOIN vente ON point_de_vente.id_point_de_vente = vente.point_de_vente_id
        GROUP BY point_de_vente.id_point_de_vente, point_de_vente.nom_point_de_vente;
    ''')
    resultats = cursor.fetchall()
    cursor.close()
    return render_template('point_de_vente/etat_point_de_vente.html', resultats=resultats)


if __name__ == '__main__':
    app.run()
