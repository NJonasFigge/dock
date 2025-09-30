
FROM nginx:alpine
WORKDIR /app


# === ARGUMENTS ===
# - ACCESS defines the htpasswd files that are allowed access to the site (comma-separated). Default: Nobody!
ARG ACCESS=""

# - FIXEDBRANCH will force the given branch, even if BRANCH will be given in environment variables.
ARG FIXEDBRANCH=""
ENV FIXEDBRANCH="$FIXEDBRANCH"

# - CGI_SCRIPTS defines the cgi scripts that shall be provided to this image from the build-cgi folder. Default: None.
ARG CGI_SCRIPTS=""

# - PROMPTHUE defines which hue (0-360) the prompt shall have. Defaults to an ugly pink.
ARG PROMPTHUE="310"


# === LAYERS ===

# - Set timezone to Berlin
RUN apk add --no-cache tzdata \
    && cp /usr/share/zoneinfo/Europe/Berlin /etc/localtime \
    && echo "Europe/Berlin" > /etc/timezone \
    && apk del tzdata

# - Install required packages
RUN apk add --no-cache git bash fcgiwrap spawn-fcgi openssh-client python3 py3-pip make

# - Make "python" point to python3
RUN ln -sf python3 /usr/bin/python

# - Deploy nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# - Activate password protection if required
COPY auth /etc/nginx/
COPY add-auth.sh /app/add-auth.sh
RUN chmod +x /app/add-auth.sh && /app/add-auth.sh "$ACCESS"

# - Deploy deployment script
COPY deploy.sh /app/deploy.sh
RUN chmod +x /app/deploy.sh

# - Deploy banner injection script
COPY inject-banner.sh /app/inject-banner.sh
RUN chmod +x /app/inject-banner.sh

# - Deploy all cgi scripts, then remove the ones that are not needed
COPY build-cgi/ /tmp/build-cgi/
RUN mkdir -p /usr/share/nginx/html/cgi
RUN for script in $(echo $CGI_SCRIPTS | tr ',' '\n'); do cp /tmp/build-cgi/$script /usr/share/nginx/html/cgi/; done
RUN rm -rf /tmp/build-cgi

# - Add github and bitbucket to known ssh hosts
RUN mkdir -p /root/.ssh && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts && \
    ssh-keyscan bitbucket.org >> /root/.ssh/known_hosts

# - Deploy entrypoint script (which will deploy the site on runtime)
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# - Install fish
RUN apk add --no-cache fish && mkdir -p /root/.config/fish
COPY config.fish /root/.config/fish/

# - Install starship and configure it
RUN curl -sS https://starship.rs/install.sh | sh -s -- -y
COPY utils ./
RUN python utils/generate_starship_toml.py $PROMPTHUE -o /root/.config/starship.toml --good-spacers

# - Set entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
