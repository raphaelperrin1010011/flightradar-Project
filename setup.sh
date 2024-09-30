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

echo "Démarrage des services Docker Compose..."
docker compose up --build -d

echo "Les services Docker Compose ont été démarrés avec succès."
echo "Vous pouvez accéder à l'application à l'adresse suivante : http://localhost:85"