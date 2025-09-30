
FROM python:3.12-slim
WORKDIR /app

# === ARGUMENTS ===

# - PROMPTHUE defines which hue (0-360) the prompt shall have. Defaults to an ugly pink.
ARG PROMPTHUE="310"

# === LAYERS ===

# - Install python3 and set python to python3
RUN apk add --no-cache python3 && \
    ln -sf /usr/bin/python3 /usr/bin/python

# - Install fish
RUN apk add --no-cache fish && mkdir -p /root/.config/fish
COPY config.fish /root/.config/fish/

# - Install starship and configure it
RUN curl -sS https://starship.rs/install.sh | sh -s -- -y
COPY utils ./utils
RUN python utils/generate_starship_toml.py $PROMPTHUE -o /root/.config/starship.toml --good-spacers
