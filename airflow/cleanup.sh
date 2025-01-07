#!/bin/bash
echo "[airflow] Arrêt et suppression des services Docker Compose..."
docker compose down

echo "[airflow] Suppression des volumes Docker..."
docker volume prune -f

echo "[airflow] Suppression des réseaux Docker non utilisés..."
docker network prune -f

echo "[airflow] Suppression du contenu de la bdd PostgreSQL et du reste..."
rm -rf logs/* plugins/* dags/__pycache__

sudo rm -rf postgres-data

echo "[airflow] Les services Docker Compose et les ressources associées ont été supprimés avec succès."
