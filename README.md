# SAE 1.04

## Connect to DB

### 1. [Install Docker](https://docs.docker.com/engine/install/)

### 2. Run start.sh

```shell
chmod ug+x start.sh
./start.sh
```

Si docker se plaint que le port 3306 est déjà utilisé, changer le port utilisé dans la commande `docker run` de `start.sh` comme suit (il faudra alors également spécifier le nouveau port dans votre `app.py`):

```
-p 3306:3306 ---> -p <nouveau_port>:3306
```

**ATTENTION :** si votre python tourne sous docker, dans `app.py`, lors de la connexion a mariadb, utiliser `host="miambiodb"` et non `host="127.0.0.1"`

## How to contribute

### 1. Create your own branch

### 2. Add your routes in the corresponding section in app.py

Each section is separated by a comment indicating the entity name

### 3. Add your templates in the corresponding folder in `templates`

One for each entity (same as in `app.py`)