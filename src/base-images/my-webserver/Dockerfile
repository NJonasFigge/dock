
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


# === Deploy oops-site ===

# - Copy oops-site files to nginx oops-html folder
RUN mkdir -p /usr/share/nginx/oops-html
COPY oops.html /usr/share/nginx/oops-html/


# === SETUP CGI-RELATED PACKAGES ===

# - Install fcgiwrap and spawn-fcgi
RUN apt-get update && \
    apt-get install -y fcgiwrap spawn-fcgi && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* \
