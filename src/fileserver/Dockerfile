
FROM python:3.12-slim
WORKDIR /app

# === ARGUMENTS ===

# - PROMPTHUE defines which hue (0-360) the prompt shall have. Defaults to an ugly pink.
ARG PROMPTHUE="310"

# === LAYERS ===

# - Install fish
RUN apt-get update && \
    apt-get install -y fish && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /root/.config/fish
COPY config.fish /root/.config/fish/

# - Install starship and configure it
RUN curl -sS https://starship.rs/install.sh | sh -s -- -y
COPY utils utils
RUN python utils/generate_starship_toml.py $PROMPTHUE -o /root/.config/starship.toml --good-spacers
