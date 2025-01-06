#!/bin/bash
echo "[airflow] Arrêt et suppression des services Docker Compose..."
docker compose down

echo "[airflow] Suppression des volumes Docker..."
docker volume prune -f

echo "[airflow] Suppression des réseaux Docker non utilisés..."
docker network prune -f

echo "[airflow] Suppression du contenu de la bdd PostgreSQL et du reste..."
rm -rf postgres-data/* logs/* plugins/* dags/__pycache__

echo "[airflow] Les services Docker Compose et les ressources associées ont été supprimés avec succès."
