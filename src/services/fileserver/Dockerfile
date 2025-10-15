
# === BASE IMAGE ===

# - Use the my-climate base image
FROM my-climate:latest
WORKDIR /app


# === ARGUMENTS ===

# - PROMPTHUE defines which hue (0-360) the prompt shall have. Defaults to an ugly pink.
ARG PROMPTHUE="310"


# === SETUP APACHE2 AND WEBDAV MODULES ===

# - Install apache2 and the required modules for WebDAV
RUN apt-get update && apt-get install -y \
    apache2 \
    apache2-utils \
    && rm -rf /var/lib/apt/lists/*

# - Enable the required apache2 modules
RUN a2enmod dav dav_fs auth_basic


# === ACTIVATE PASSWORD PROTECTION ===

# - Deploy htpasswd file
COPY .htpasswd /etc/apache2/.htpasswd


# === CONFIGURE APACHE2 FOR WEBDAV ===

# - Copy the apache2 configuration file for WebDAV into the sites-available folder
COPY dav.conf /etc/apache2/sites-available/000-default.conf

# - Set the ServerName to localhost to avoid warning messages
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf


# === ACTIVATE CUSTOM STARSHIP CONFIGURATION ===

# - Generate starship configuration with the given prompt hue inside the .config folder of the root user
RUN python starship-utils/generate_starship_toml.py $PROMPTHUE -o /root/.config/starship.toml --good-spacers


# === PREPARE WEBDAV DIRECTORY ===

# - Create a directory for webdav files
RUN mkdir -p /var/webdav && \
    chown www-data:www-data /var/webdav && \
    chmod 755 /var/webdav


# === PREPARE LOG DIRECTORY ===

# - Create a log directory for webdav logs
RUN mkdir -p /var/log/webdav && \
    chown www-data:www-data /var/log/webdav && \
    chmod 755 /var/log/webdav


# === EXTEND ABOUT FILE ===

# - Deploy about file extension
COPY about-this-service.md /tmp/about-this-service-extension.md

# - Append to about file
RUN cat /tmp/about-this-service-extension.md >> /app/about-this-service.md && \
    rm /tmp/about-this-service-extension.md


# === SET COMMAND ===

# - Start apache server in foreground (so that the container doesn't exit)
CMD ["apachectl", "-D", "FOREGROUND"]
