from flask import Flask, request, render_template, redirect, flash
import datetime

app = Flask(__name__)
app.secret_key = 'une_cle_secrete'
app.secret_key = 'une cle(token) : grain de sel(any random string)'
app.config["TEMPLATES_AUTO_RELOAD"] = True

  ## à ajouter
from flask import session, g
import pymysql.cursors

def get_db():
    if 'db' not in g:
        g.db =  pymysql.connect(
            host="serveurmysql.iut-bm.univ-fcomte.fr",  # localhost sur les machines perso.
            user="adessaux",
            password="secret",
            database="BDD_adessaux_sae",
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
def index():

    return render_template('layout.html', )

@app.route('/vente/show')
def show_ventes():
    mycursor = get_db().cursor()
    sql = '''
          SELECT vente.id_vente  AS id
                , vente.date_vente
                , vente.heure_debut
                , vente.heure_fin
                , vente.point_de_vente_id AS ptVente_id
                , point_de_vente.nom_point_de_vente
           FROM vente
            INNER JOIN point_de_vente ON vente.point_de_vente_id = point_de_vente.id_point_de_vente
           ORDER BY vente.id_vente ASC;
        '''
    mycursor.execute(sql)
    liste_ventes = mycursor.fetchall()
    return render_template('vente/show_vente.html', ventes=liste_ventes)


@app.route('/vente/add', methods=['GET'])
def add_vente():
    mycursor = get_db().cursor()
    sql = ("""
           SELECT id_point_de_vente AS id, nom_point_de_vente
           FROM point_de_vente
           ORDER BY id;

         """)
    mycursor.execute(sql)
    liste_ptdeVentes = mycursor.fetchall()
    return render_template('vente/add_vente.html', ptdeVente=liste_ptdeVentes)


@app.route('/vente/delete')
def delete_vente():
    print('''suppression d'une vente''')
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql = ("""DELETE
              FROM vente
              WHERE id_vente = %s;""")
    mycursor.execute(sql, (id,))
    get_db().commit()
    message = 'Suppression de l\'étudiant d\'identifiant :' + str(id)
    print(message)
    flash(message, 'alert-warning')
    return redirect('/vente/show')


@app.route('/vente/edit', methods=['GET'])
def edit_vente():
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql = ("""SELECT 
                    vente.id_vente AS id
                   ,vente.date_vente
                   , TIME_FORMAT(vente.heure_debut, '%%H:%%i') as heure_debut
                   , TIME_FORMAT(vente.heure_fin, '%%H:%%i') as heure_fin
                   , vente.point_de_vente_id as id_pdv
              FROM vente
              WHERE id_vente = %s;
           """)
    mycursor.execute(sql, (id,))
    nom_vente = mycursor.fetchone()
    sql = ("""
           SELECT id_point_de_vente AS id, nom_point_de_vente
           FROM point_de_vente
           ORDER BY id;
           """)
    mycursor.execute(sql)
    listeptdeVente = mycursor.fetchall()
    return render_template('vente/edit_vente.html', vente=nom_vente, ptdeVente=listeptdeVente)


@app.route('/vente/add', methods=['POST'])
def valid_add_vente():
    id_pdv = request.form.get('id_pdv')
    date_vente = request.form.get('date_vente')
    heure_debut = request.form.get('heure_debut')
    heure_fin = request.form.get('heure_fin')
    tuple_insert = (date_vente, heure_debut, heure_fin, id_pdv)
    mycursor = get_db().cursor()

    sql = ("""INSERT INTO vente (date_vente, heure_debut, heure_fin, point_de_vente_id)
VALUES (%s, %s,%s, %s);""")
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    message = 'Ajout d\'une vente au point de vente n°' + str(id_pdv) + ' - à la date :' + str(date_vente)
    flash(message, 'alert-success')
    return redirect('/vente/show')


@app.route('/vente/edit', methods=['POST'])
def valid_edit_vente():
    id =request.form.get('id')
    id_pdv = request.form.get('id_pdv')
    date_vente = request.form.get('date_vente')
    heure_debut = request.form.get('heure_debut')
    heure_fin = request.form.get('heure_fin')
    tuple_insert = (date_vente, heure_debut, heure_fin, id_pdv,id)
    mycursor = get_db().cursor()
    sql = ("""UPDATE vente
              SET date_vente     = %s,
                  heure_debut = %s,
                  heure_fin = %s,
                  point_de_vente_id = %s
              WHERE id_vente = %s;""")
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    message = 'Modification d\'une vente au point de vente n°' + str(id_pdv) + ' - à la date :' + str(date_vente)
    flash(message, 'alert-success')
    return redirect('/vente/show')

@app.route('/vente/details',methods=['GET'])
def details_vente():
    id = request.args.get('id')
    mycursor = get_db().cursor()

    #requète vente
    sql = '''
                SELECT vente.id_vente                            AS id
                     , vente.date_vente
                     , TIME_FORMAT(vente.heure_debut, '%%H:%%i') AS heure_debut
                     , TIME_FORMAT(vente.heure_fin, '%%H:%%i')   AS heure_fin
                     , point_de_vente.nom_point_de_vente
                     , point_de_vente.adresse_point_de_vente
                     , ville.nom_ville
                FROM vente
                         INNER JOIN point_de_vente ON vente.point_de_vente_id = point_de_vente.id_point_de_vente
                         INNER JOIN ville ON point_de_vente.ville_id = ville.id_ville
                WHERE vente.id_vente = %s; \
                '''
    mycursor.execute(sql, (id,))
    vente = mycursor.fetchone()

    # requete maraicher
    sql = '''
        SELECT m.id_maraicher,
               m.prenom,
               m.nom,
               m.raison_sociale,
               m.telephone,
               m.numero_bio,
               COUNT(a.produit_id) AS nb_produits,
               ROUND(AVG(a.prix_produit), 2) AS prix_moyen,
               COALESCE(SUM(a.quantite_vendue), 0) AS total_vendu
        FROM maraicher m
        INNER JOIN annonce a ON m.id_maraicher = a.maraicher_id
        WHERE a.vente_id = %s
        GROUP BY m.id_maraicher, m.prenom, m.nom, m.raison_sociale, m.telephone, m.numero_bio
        ORDER BY nb_produits DESC, m.nom ASC;
    '''
    mycursor.execute(sql, (id,))
    listes_maraichers = mycursor.fetchall()
    #requète produit
    sql = '''
        SELECT p.id_produit,
               p.nom_produit,
               tp.nom_type_produit,
               u.nom_unite,
               COUNT(DISTINCT a.maraicher_id) AS nb_maraichers,
               ROUND(AVG(a.prix_produit), 2) AS prix_moyen,
               MIN(a.prix_produit) AS prix_min,
               MAX(a.prix_produit) AS prix_max,
               COALESCE(SUM(a.quantite_vendue), 0) AS quantite_totale
        FROM annonce a
        INNER JOIN produit p ON a.produit_id = p.id_produit
        INNER JOIN type_produit tp ON p.type_produit_id = tp.id_type_produit
        INNER JOIN unite u ON a.unite_id = u.id_unite
        WHERE a.vente_id = %s
        GROUP BY p.id_produit, p.nom_produit, tp.nom_type_produit, u.id_unite, u.nom_unite
        ORDER BY p.nom_produit ASC;
        '''
    mycursor.execute(sql, (id,))
    liste_produits = mycursor.fetchall()
    #bilan :
    sql = """
                SELECT COALESCE(SUM(a.quantite_vendue), 0)                                        AS nb_produits_vendus,
                       COUNT(DISTINCT a.produit_id)                                               AS nb_varietes_produits,
                       COALESCE(SUM(a.prix_produit * a.quantite_vendue), 0)                       AS chiffre_affaires,
                       pdv.tarifs_location,
                       COALESCE(SUM(a.prix_produit * a.quantite_vendue), 0) - pdv.tarifs_location AS benefice
                -- Variante si chaque maraîcher paie l'emplacement :
                -- COALESCE(SUM(a.prix_produit * a.quantite_vendue), 0) - (pdv.tarifs_location * COUNT(DISTINCT a.maraicher_id)) AS benefice
                FROM vente v
                         INNER JOIN point_de_vente pdv ON v.point_de_vente_id = pdv.id_point_de_vente
                         LEFT JOIN annonce a ON v.id_vente = a.vente_id
                WHERE v.id_vente = %s
                GROUP BY v.id_vente, pdv.tarifs_location; \
                """
    mycursor.execute(sql, (id,))
    bilan = mycursor.fetchone()
    return render_template('vente/details_vente.html',bilan=bilan,vente=vente,  maraichers=listes_maraichers, produits=liste_produits)

@app.route('/vente/etat', methods=['GET'])
def etat_vente():
    id_pdv = request.args.get('id_pdv')
    mycursor = get_db().cursor()

    # 1. Liste des points de vente pour le menu déroulant
    sql = """
          SELECT id_point_de_vente AS id, nom_point_de_vente
          FROM point_de_vente
          ORDER BY id;
          """
    mycursor.execute(sql)
    liste_ptdeVentes = mycursor.fetchall()

    # 2. Liste des créneaux pour le point de vente choisi
    sql = """
          SELECT vente.id_vente AS id,
                 vente.date_vente,
                 TIME_FORMAT(vente.heure_debut, '%%H:%%i') AS heure_debut,
                 TIME_FORMAT(vente.heure_fin, '%%H:%%i') AS heure_fin,
                 point_de_vente.nom_point_de_vente
          FROM vente
          INNER JOIN point_de_vente ON vente.point_de_vente_id = point_de_vente.id_point_de_vente
          WHERE vente.point_de_vente_id = %s
          ORDER BY vente.date_vente ASC;
          """
    mycursor.execute(sql, (id_pdv,))
    liste_ventes = mycursor.fetchall()

    # 3. Nombre de créneaux de vente
    sql = """
          SELECT COUNT(vente.id_vente) AS nb_ventes,
                 point_de_vente.nom_point_de_vente
          FROM point_de_vente
          LEFT JOIN vente ON vente.point_de_vente_id = point_de_vente.id_point_de_vente
          WHERE point_de_vente.id_point_de_vente = %s
          GROUP BY point_de_vente.id_point_de_vente, point_de_vente.nom_point_de_vente;
          """
    mycursor.execute(sql, (id_pdv,))
    bilan = mycursor.fetchone()

    return render_template(
        'vente/etat_vente.html', ptdeVente=liste_ptdeVentes, ventes=liste_ventes, bilan=bilan, id_pdv=id_pdv)



if __name__ == '__main__':
    app.run(debug=True, port=5000)

