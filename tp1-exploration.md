# TP1 : exploration des API

## API Docker

```bash
D=http://127.0.0.1:2375
```

### 1. Version de Docker

```bash
curl -s $D/version
```

Code : 200

Docker répond en JSON avec sa version (29.10.0) et la version de l'API (1.57).

### 2. Lister tous les conteneurs

```bash
curl -s "$D/containers/json?all=true"
```

Code : 200

Ce que ça renvoie : tout

À quoi sert `all=true` : renvoi tout

### 3. Lister seulement les conteneurs étiquetés

```bash
curl -s --get $D/containers/json --data-urlencode 'all=true' \
     --data-urlencode 'filters={"label":["adminapi.managed=true"]}'
```

Code : 200

Ce que ça renvoie : celui avec le label adminadpi.managed=true

### 4. Détail de web1

```bash
curl -s $D/containers/web1/json
```

Code : 200

Ce que ça renvoie : le containeurs web1 en json

### 5. Démarrer web1

```bash
curl -i -X POST $D/containers/web1/start
```

Code : 204

Ce que ça veut dire : containers lancer

### 6. Arrêter web1

```bash
curl -i -X POST $D/containers/web1/stop
```

Code : 204

Ce que ça veut dire : containeurs arreter

### 7. Arrêter web1 une deuxième fois

```bash
curl -i -X POST $D/containers/web1/stop
```

Code : 304

Pourquoi ce code est différent de celui de la commande 6 : ccar il est déjà arreter

### 8. Conteneur inexistant

```bash
curl -i $D/containers/nimportequoi/json
```

Code : 404

Ce que ça veut dire : il trouve pas le containers


