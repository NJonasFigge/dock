
# === BASE IMAGE ===

# - Use the my-webserver base image
FROM my-webserver:latest
WORKDIR /app


# === ARGUMENTS ===

# - PROMPTHUE defines which hue (0-360) the prompt shall have. Defaults to an ugly pink.
ARG PROMPTHUE="310"


# === DEPLOY NGINX CONFIGURATION ===

# - Deploy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf


# === ACTIVATE CUSTOM STARSHIP CONFIGURATION ===

# - Generate starship configuration with the given prompt hue inside the .config folder of the root user
RUN python starship-utils/generate_starship_toml.py $PROMPTHUE -o /root/.config/starship.toml --good-spacers


# === EXTEND ABOUT FILE ===

# - Deploy about file extension
COPY about-this-service.md /tmp/about-this-service-extension.md

# - Append to about file
RUN cat /tmp/about-this-service-extension.md >> /app/about-this-service.md && \
    rm /tmp/about-this-service-extension.md


# === SET COMMAND ===

# - Start nginx server in foreground (so that the container doesn't exit)
CMD ["nginx", "-g", "daemon off;"]
