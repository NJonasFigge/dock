
FROM python:3.12-slim
WORKDIR /app

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
