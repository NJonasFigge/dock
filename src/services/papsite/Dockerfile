
# === BASE IMAGE ===

# - Use the papsite base image
FROM papsite-base:latest
WORKDIR /app


# === ARGUMENTS ===

# - ACCESS defines the htpasswd files that are allowed access to the site (comma-separated). Default: Nobody!
ARG ACCESS=""

# - CGI_SCRIPTS defines the cgi scripts that shall be provided to this image from the build-cgi folder. Default: None.
ARG CGI_SCRIPTS=""

# - PROMPTHUE defines which hue (0-360) the prompt shall have. Defaults to an ugly pink.
ARG PROMPTHUE="310"

# - FIXEDBRANCH will force the given branch, even if BRANCH will be given in environment variables.
ARG FIXEDBRANCH=""
ENV FIXEDBRANCH="$FIXEDBRANCH"


# === DEPLOY NGINX CONFIGURATION ===

# - Deploy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf


# === ACTIVATE NGINX PASSWORD PROTECTION ===

# - Run the add-auth script to deploy the htpasswd files and configure nginx
RUN ./add-auth.sh "$ACCESS"


# === DEPLOY REQUESTED CGI SCRIPTS ===

# - Create CGI destination folder
RUN mkdir -p /usr/share/nginx/html/cgi

# - Copy requested cgi scripts from build-cgi folder to nginx cgi folder
RUN for script in $(echo $CGI_SCRIPTS | tr ',' '\n'); do cp /tmp/build-cgi/$script /usr/share/nginx/html/cgi/; done

# - Remove build-cgi folder (no longer needed)
RUN rm -rf /tmp/build-cgi


# === ACTIVATE CUSTOM STARSHIP CONFIGURATION ===

# - Generate starship configuration with the given prompt hue inside the .config folder of the root user
RUN python starship-utils/generate_starship_toml.py $PROMPTHUE -o /root/.config/starship.toml --good-spacers


# === SET ENTRYPOINT ===

# - Set entrypoint script
ENTRYPOINT ["entrypoint.sh"]
