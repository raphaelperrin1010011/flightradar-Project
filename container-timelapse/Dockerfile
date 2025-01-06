FROM continuumio/miniconda3

# Créer et activer l'environnement Conda
RUN conda create -n myenv python=3.9 -y
RUN echo "source activate myenv" > ~/.bashrc
ENV PATH /opt/conda/envs/myenv/bin:$PATH

# Installation des dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libproj-dev \
    proj-data \
    proj-bin \
    libgdal-dev \
    gdal-bin \
    libgeos-dev \
    libexpat1 \
    libexpat1-dev \
    libjpeg-dev \
    libpng-dev \
    libz-dev \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Configuration des variables d'environnement pour GDAL et PROJ
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal
ENV PROJ_LIB=/usr/share/proj

# Copie du code source
COPY . /app
WORKDIR /app

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Exposition du port de l'application
EXPOSE 5000

# Commande par défaut pour lancer l'application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]