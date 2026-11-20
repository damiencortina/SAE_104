USE BDD_nfaouz;

DROP TABLE IF EXISTS annonce;
DROP TABLE IF EXISTS pousse_en;
DROP TABLE IF EXISTS recolte;
DROP TABLE IF EXISTS vente;
DROP TABLE IF EXISTS point_de_vente;
DROP TABLE IF EXISTS produit;
DROP TABLE IF EXISTS unite;
DROP TABLE IF EXISTS ville;
DROP TABLE IF EXISTS semaine;
DROP TABLE IF EXISTS saison;
DROP TABLE IF EXISTS type_produit;
DROP TABLE IF EXISTS maraicher;

CREATE TABLE maraicher
(
    id_maraicher   BIGINT AUTO_INCREMENT,
    prenom         VARCHAR(255) NOT NULL,
    nom            VARCHAR(255) NOT NULL,
    telephone      CHAR(10)     NOT NULL,
    raison_sociale VARCHAR(255),
    email          VARCHAR(255),
    numero_bio     VARCHAR(10),
    PRIMARY KEY (id_maraicher)
);

CREATE TABLE type_produit
(
    id_type_produit  INT AUTO_INCREMENT,
    nom_type_produit VARCHAR(50),
    PRIMARY KEY (id_type_produit)
);

CREATE TABLE saison
(
    id_saison  TINYINT AUTO_INCREMENT,
    nom_saison VARCHAR(10),
    PRIMARY KEY (id_saison)
);

CREATE TABLE semaine
(
    id_semaine     INT AUTO_INCREMENT,
    numero_semaine TINYINT  NOT NULL,
    annee          SMALLINT NOT NULL,
    PRIMARY KEY (id_semaine)
);

CREATE TABLE ville
(
    id_ville  INT AUTO_INCREMENT,
    nom_ville VARCHAR(255),
    PRIMARY KEY (id_ville)
);

CREATE TABLE unite
(
    id_unite  TINYINT AUTO_INCREMENT,
    nom_unite VARCHAR(255),
    PRIMARY KEY (id_unite)
);

CREATE TABLE produit
(
    id_produit      INT AUTO_INCREMENT,
    nom_produit     VARCHAR(255),
    type_produit_id INT NOT NULL,
    PRIMARY KEY (id_produit),
    FOREIGN KEY (type_produit_id) REFERENCES type_produit (id_type_produit)
);

CREATE TABLE point_de_vente
(
    id_point_de_vente          INT AUTO_INCREMENT,
    nom_point_de_vente         VARCHAR(255),
    adresse_point_de_vente     VARCHAR(255),
    code_postal_point_de_vente VARCHAR(5),
    ville_id                   INT NOT NULL,
    maraicher_id               BIGINT,
    PRIMARY KEY (id_point_de_vente),
    FOREIGN KEY (ville_id) REFERENCES ville (id_ville),
    FOREIGN KEY (maraicher_id) REFERENCES maraicher (id_maraicher)
);

CREATE TABLE vente
(
    id_vente          INT AUTO_INCREMENT,
    date_vente        DATE,
    heure_debut       TIME,
    heure_fin         TIME,
    point_de_vente_id INT NOT NULL,
    PRIMARY KEY (id_vente),
    FOREIGN KEY (point_de_vente_id) REFERENCES point_de_vente (id_point_de_vente)
);

CREATE TABLE recolte
(
    maraicher_id      BIGINT,
    produit_id        INT,
    unite_id          TINYINT,
    semaine_id        INT,
    quantite_recoltee INT,
    PRIMARY KEY (maraicher_id, produit_id, unite_id, semaine_id),
    FOREIGN KEY (maraicher_id) REFERENCES maraicher (id_maraicher),
    FOREIGN KEY (produit_id) REFERENCES produit (id_produit),
    FOREIGN KEY (unite_id) REFERENCES unite (id_unite),
    FOREIGN KEY (semaine_id) REFERENCES semaine (id_semaine)
);

CREATE TABLE pousse_en
(
    produit_id INT,
    saison_id  TINYINT,
    PRIMARY KEY (produit_id, saison_id),
    FOREIGN KEY (produit_id) REFERENCES produit (id_produit),
    FOREIGN KEY (saison_id) REFERENCES saison (id_saison)
);

CREATE TABLE annonce
(
    maraicher_id    BIGINT,
    produit_id      INT,
    vente_id        INT,
    unite_id        TINYINT,
    prix_produit    SMALLINT,
    quantite_vendue SMALLINT,
    PRIMARY KEY (maraicher_id, produit_id, vente_id, unite_id),
    FOREIGN KEY (maraicher_id) REFERENCES maraicher (id_maraicher),
    FOREIGN KEY (produit_id) REFERENCES produit (id_produit),
    FOREIGN KEY (vente_id) REFERENCES vente (id_vente),
    FOREIGN KEY (unite_id) REFERENCES unite (id_unite)
);

INSERT INTO maraicher (prenom, nom, telephone, raison_sociale, email, numero_bio)
VALUES ("Damien", "Cortina", "0102030405", "Même pomme'al !", "mail@mail.fr", "FR-BIO-01"),
       ("Arthur", "Dessaux", "0102030405", "Chez Arthur", "mail@mail.fr", "FR-BIO-01"),
       ("Tom", "Creusot--Duc", "0102030405", "Le Potager du Doubs", "mail@mail.fr", "FR-BIO-01"),
       ("Noah", "Faouz", "0102030405", "Champ pour Champ", "mail@mail.fr", "FR-BIO-01");

INSERT INTO type_produit (nom_type_produit)
VALUES ("Fruit"),
       ("Légume");

INSERT INTO saison (nom_saison)
VALUES ("Printemps"),
       ("Éte"),
       ("Automne"),
       ("Hiver");

INSERT INTO semaine (numero_semaine, annee)
VALUES (16, 2026),
       (17, 2026),
       (18, 2026),
       (19, 2026),
       (20, 2026),
       (21, 2026);

INSERT INTO ville (nom_ville)
VALUES ("Belfort"),
       ("Montbéliard"),
       ("Toulouse");

INSERT INTO unite (nom_unite)
VALUES ("kg"),
       ("tonne"),
       ("pièce");

INSERT INTO produit (nom_produit, type_produit_id)
VALUES ("Pomme", 1),
       ("Pomme de terre", 2),
       ("Concombre", 2),
       ("Carotte", 2),
       ("Pastèque", 1);

INSERT INTO point_de_vente (nom_point_de_vente, adresse_point_de_vente, code_postal_point_de_vente, ville_id,
                            maraicher_id)
VALUES ("Marché des Résidences", "Boulevard Kenedy", 90000, 1, NULL),
       ("Marché de Montbeliard", "Place du Marché", 25200, 2, NULL),
       ("Ferme de DD", "5 rue des Chocolatines", 31300, 3, 1),
       ("La Seconde Ferme de DD", "12 rue des Croissants", 31300, 3, 1);

INSERT INTO vente (date_vente, heure_debut, heure_fin, point_de_vente_id)
VALUES ("2026-06-03", "07:00:00", "12:00:00", 1),
       ("2026-06-10", "07:00:00", "12:00:00", 1),
       ("2026-06-17", "07:00:00", "12:00:00", 1),
       ("2026-06-24", "07:00:00", "12:00:00", 1),
       ("2026-06-02", "06:00:00", "13:00:00", 2),
       ("2026-06-09", "06:00:00", "13:00:00", 2),
       ("2026-06-16", "06:00:00", "13:00:00", 2),
       ("2026-06-23", "06:00:00", "13:00:00", 2),
       ("2026-06-10", "06:00:00", "21:00:00", 3);

INSERT INTO recolte (maraicher_id, produit_id, unite_id, semaine_id, quantite_recoltee)
VALUES (1, 1, 2, 1, 12),
       (1, 4, 1, 1, 50),
       (2, 2, 2, 2, 20),
       (2, 2, 2, 1, 35),
       (3, 2, 2, 1, 14),
       (3, 4, 2, 3, 200),
       (4, 5, 2, 3, 10);

INSERT INTO pousse_en (produit_id, saison_id)
VALUES (1, 1),
       (1, 2),
       (2, 2),
       (3, 1),
       (3, 2),
       (4, 3),
       (4, 4),
       (5, 2);

INSERT INTO annonce (maraicher_id, produit_id, vente_id, unite_id, prix_produit, quantite_vendue)
VALUES (1, 1, 9, 1, 2, 50),
       (2, 2, 1, 1, 12, NULL),
       (2, 3, 1, 1, 25, NULL),
       (2, 2, 2, 1, 12, NULL),
       (2, 3, 2, 1, 22, NULL),
       (3, 3, 1, 1, 24, NULL),
       (4, 5, 1, 3, 50, NULL);

# Liste des maraîchers proposant une vente à domicile
SELECT m.prenom, m.nom, m.raison_sociale, COUNT(*) AS nombre_de_pdv FROM maraicher m
JOIN point_de_vente pdv ON m.id_maraicher = pdv.maraicher_id
GROUP BY m.prenom, m.nom, m.raison_sociale;

# Liste des produits proposés au Marché des Residences du 3 Juin 2026
SELECT produit.nom_produit AS produits_proposes, COUNT(produit.id_produit) AS nb_maraichers FROM produit
JOIN annonce a ON produit.id_produit = a.produit_id
JOIN vente v ON a.vente_id = v.id_vente
JOIN point_de_vente pdv ON v.point_de_vente_id = pdv.id_point_de_vente
WHERE pdv.nom_point_de_vente = "Marché des Residences" AND v.date_vente = "2026-06-03"
GROUP BY produit.nom_produit;

# Liste des produits récoltés lors de la semaine 16, dans l'ordre alphabétique
SELECT p.nom_produit AS produits_recoltes_S16 FROM produit p
JOIN recolte r ON p.id_produit = r.produit_id
JOIN semaine s ON r.semaine_id = s.id_semaine
WHERE s.numero_semaine = 16
GROUP BY p.nom_produit;

# Liste des producteurs de Pomme de Terre
SELECT m.nom, m.prenom, m.raison_sociale FROM maraicher m
JOIN recolte r ON m.id_maraicher = r.maraicher_id
JOIN produit p ON r.produit_id = p.id_produit
WHERE p.nom_produit = "Pomme de terre"
GROUP BY m.nom, m.prenom, m.raison_sociale;

# Liste des producteurs cultivant des produits poussant en hiver
SELECT m.nom, m.prenom, m.raison_sociale FROM maraicher m
JOIN recolte r ON m.id_maraicher = r.maraicher_id
JOIN produit p ON r.produit_id = p.id_produit
JOIN pousse_en pe ON p.id_produit = pe.produit_id
JOIN saison s ON pe.saison_id = s.id_saison
WHERE s.nom_saison = "Hiver"
GROUP BY m.nom, m.prenom, m.raison_sociale;