#!/bin/bash

if ! command -v docker &> /dev/null
then
    echo "Docker n'est pas installé. Veuillez installer Docker d'abord."
    exit 1
fi

if ! command -v docker compose &> /dev/null
then
    echo "Docker Compose n'est pas installé. Veuillez installer Docker Compose d'abord."
    exit 1
fi

echo "Initialisation de la base de données Airflow..."

cd airflow

sh setup.sh && docker network prune -f && sh run.sh

cd ..

while ! docker network ls | grep -q "airflow_app-network"; do
    echo "Attente de la création du réseau airflow_app-network..."
    sleep 2
done

docker compose up --build

echo "Les services Docker Compose ont été démarrés avec succès."

echo "Vous pouvez accéder à l'application à l'adresse suivante : http://localhost:85"