
FROM python:3.12-slim
WORKDIR /app

# === ARGUMENTS ===

# - PROMPTHUE defines which hue (0-360) the prompt shall have. Defaults to an ugly pink.
ARG PROMPTHUE="310"

# === LAYERS ===

# - REPO defines which git repo the telegram bot is in
ARG REPO=""
ENV REPO="$REPO"

# - Deploy entrypoint script (which will deploy the site on runtime)
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# - Install required packages
RUN apt-get update && \
    apt-get install -y fish openssh-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# - Deploy fish configuration
RUN mkdir -p /root/.config/fish
COPY config.fish /root/.config/fish/

# - Install starship and configure it
RUN curl -sS https://starship.rs/install.sh | sh -s -- -y
COPY utils ./utils
RUN python utils/generate_starship_toml.py $PROMPTHUE -o /root/.config/starship.toml --good-spacers

# - Add github and bitbucket to known ssh hosts
RUN mkdir -p /root/.ssh && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts && \
    ssh-keyscan bitbucket.org >> /root/.ssh/known_hosts

# - Set entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
