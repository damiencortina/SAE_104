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
    message = 'Ajout d\'une vente au point de vente n°' + str(id) + ' - à la date :' + str(date_vente)
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


if __name__ == '__main__':
    app.run(debug=True, port=5000)

