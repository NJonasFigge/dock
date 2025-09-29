
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

# - Install fish
RUN apk add --no-cache fish && mkdir -p /root/.config/fish
COPY config.fish /root/.config/fish/

# - Install starship and configure it
RUN curl -sS https://starship.rs/install.sh | sh -s -- -y
COPY generate_starship_toml.py /tmp/generate_starship_toml.py
COPY starship_template.toml /tmp/starship_template.toml
RUN python /tmp/generate_starship_toml.py $PROMPTHUE -o /root/.config/starship.toml --good-spacers

# - Generate ssh keys
RUN ssh-keygen -t rsa -b 4096 -f /root/.ssh/id_rsa -N "" -C "papsite-deploy-key"
RUN chmod 600 /root/.ssh/id_rsa

# - Set entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
