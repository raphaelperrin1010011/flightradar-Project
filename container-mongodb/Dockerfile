# Utiliser l'image officielle de MongoDB comme image de base
FROM mongo:latest

# Installer Python pour générer le mot de passe
RUN apt-get update && apt-get install -y python3

# Copier le script d'entrée
COPY entrypoint.sh /entrypoint.sh

# Rendre le script exécutable
RUN chmod +x /entrypoint.sh

# Exposer le port par défaut de MongoDB
EXPOSE 27017

# Utiliser le script d'entrée comme point d'entrée
ENTRYPOINT ["/entrypoint.sh"]