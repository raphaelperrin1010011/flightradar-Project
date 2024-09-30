# Utiliser une image de base officielle de Python
FROM python:3.9-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers requirements.txt et stream.py dans le conteneur
COPY . /app
# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Définir la commande pour exécuter l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]