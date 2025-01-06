echo "[airflow] Création des répertoires nécessaires..."
mkdir postgres-data

echo "[airflow] Initialisation de la base de données"
docker compose up airflow-init
