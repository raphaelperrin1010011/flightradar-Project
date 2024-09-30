#!/bin/bash

# Générer un mot de passe complexe
PASSWORD=$(python3 -c "import random, string; print(''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for i in range(16)))")

# Exporter les variables d'environnement pour MongoDB
export MONGO_INITDB_ROOT_USERNAME=admin
export MONGO_INITDB_ROOT_PASSWORD=$PASSWORD

# Démarrer MongoDB
exec mongod