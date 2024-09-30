# Utiliser une image de base Python
FROM python:3.9-slim

# Installer les dépendances nécessaires
RUN apt-get update && \
    apt-get install -y wget gnupg unzip curl && \
    apt-get install -y libnss3 libgconf-2-4 libxi6 libxrandr2 libxss1 libxcursor1 libxcomposite1 libasound2 libatk1.0-0 libpangocairo-1.0-0 libgtk-3-0 libxdamage1 libxext6 libxfixes3 libxrender1 libxtst6 xdg-utils

# Installer Chrome
RUN wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' && \
    apt-get update && \
    apt-get install -y google-chrome-stable

# Installer ChromeDriver spécifique
RUN wget -O /tmp/chromedriver.zip https://storage.googleapis.com/chrome-for-testing-public/129.0.6668.58/linux64/chromedriver-linux64.zip && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    chmod +x /tmp/chromedriver-linux64/chromedriver && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver

# Définir la variable d'environnement pour le driver Chrome
ENV webdriver.chrome.driver=/usr/local/bin/chromedriver

# Copier les fichiers de l'application
COPY . /app
WORKDIR /app
RUN mkdir -p /app/screenshots

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Commande pour démarrer l'application
CMD ["uvicorn", "scrap_image:app", "--host", "0.0.0.0", "--port", "8200"]