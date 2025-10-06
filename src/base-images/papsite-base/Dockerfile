
# === BASE IMAGE ===

# - Use the my-webserver base image
FROM my-webserver:latest


# === PREPARE NGINX PASSWORD PROTECTION TOOLS ===

# - Deploy auth files
COPY auth /etc/nginx/auth

# - Deploy activation script
COPY add-auth.sh ./

# - Make activation script runnable
RUN chmod +x add-auth.sh


# === PREPARE PAPSITE DEPLOYMENT ===

# - Deploy deployment script
COPY deploy.sh ./

# - Make deployment script runnable
RUN chmod +x deploy.sh


# === PREPARE BANNER INJECTION ===

# - Deploy banner injection script
COPY inject-banner.sh ./

# - Make banner injection script runnable
RUN chmod +x inject-banner.sh


# === PREPARE CGI SCRIPTS ===

# - Deploy all cgi scripts to a temporary directory
COPY build-cgi /tmp/build-cgi

# - Make all cgi scripts runnable
RUN chmod +x /tmp/build-cgi/*


# === PREPARE ENTRYPOINT SCRIPT ===

# - Deploy entrypoint script (which will deploy the website on runtime)
COPY entrypoint.sh ./

# - Make entrypoint script runnable
RUN chmod +x entrypoint.sh
