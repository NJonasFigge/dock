
# === BASE IMAGE ===

# - Use the my-climate base image
FROM my-climate:latest


# === SETUP NGINX ===

# - Install nginx
RUN apt-get update && \
    apt-get install -y nginx && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# - Remove default nginx configuration
RUN rm /etc/nginx/sites-enabled/default

# - Deploy custom nginx configuration
COPY nginx.conf /etc/nginx/sites-available/papierschiffdieband.de.conf


# === SETUP CGI-RELATED PACKAGES ===

# - Install fcgiwrap and spawn-fcgi
RUN apt-get update && \
    apt-get install -y fcgiwrap spawn-fcgi && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* \
