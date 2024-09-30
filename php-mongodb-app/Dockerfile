# Utiliser l'image officielle PHP avec Apache
FROM php:8.1-apache

# Installer les dépendances nécessaires
RUN apt-get update && apt-get install -y \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libonig-dev \
    libzip-dev \
    unzip \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install gd mbstring zip

# Installer l'extension MongoDB
RUN pecl install mongodb && docker-php-ext-enable mongodb


# Installer Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Copier les fichiers de l'application dans le conteneur
COPY . /var/www/html/

#lancer l'install de composer
RUN composer install

# Copier la configuration Apache personnalisée
COPY apache-config.conf /etc/apache2/sites-available/000-default.conf

# Définir les permissions appropriées
RUN chown -R www-data:www-data /var/www/html \
    && chmod -R 755 /var/www/html

# Exposer le port 85
EXPOSE 85

# Démarrer Apache
CMD ["apache2-foreground"]