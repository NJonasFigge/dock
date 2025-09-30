
FROM nginx:alpine
WORKDIR /app

# === ARGUMENTS ===

# - PROMPTHUE defines which hue (0-360) the prompt shall have. Defaults to an ugly pink.
ARG PROMPTHUE="310"

# === LAYERS ===

# - Install bash
RUN apk add --no-cache bash

# - Deploy nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# - Install fish
RUN apk add --no-cache fish && mkdir -p /root/.config/fish
COPY config.fish /root/.config/fish/

# - Install starship and configure it
RUN curl -sS https://starship.rs/install.sh | sh -s -- -y
COPY utils ./utilsutils
RUN python utils/generate_starship_toml.py $PROMPTHUE -o /root/.config/starship.toml --good-spacers

# - Entry by starting the nginx server
CMD ["nginx", "-g", "daemon off;"]
