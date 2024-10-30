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

echo "Arrêt et suppression des services Docker Compose..."
docker compose down

echo "Suppression des volumes Docker..."
docker volume prune -f

echo "Suppression des réseaux Docker non utilisés..."
docker network prune -f

cd airflow
sh cleanup.sh

echo "Les services Docker Compose et les ressources associées ont été supprimés avec succès."
