
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
RUN apk add --no-cache fish && mkdir -p ~/.config/fish && chsh -s /usr/bin/fish
COPY ../../system-setup/config.fish ~/.config/fish/

# - Install starship and configure it
RUN curl -sS https://starship.rs/install.sh | sh -s -- -y
COPY ../../utils/generate_starship_toml.py /tmp/generate_starship_toml.py
COPY ../../utils/starship_template.toml /tmp/starship_template.toml
RUN python /tmp/generate_starship_toml.py $PROMPTHUE -o ~/.config/starship.toml --good-spacers

# - Set entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
