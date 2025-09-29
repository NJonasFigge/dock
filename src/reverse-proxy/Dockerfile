
FROM nginx:alpine

# === ARGUMENTS ===

# - PROMPTHUE defines which hue (0-360) the prompt shall have. Defaults to an ugly pink.
ARG PROMPTHUE="310"

# === LAYERS ===

# - Install bash
RUN apk add --no-cache bash

# - Deploy nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# - Install fish
RUN apk add --no-cache fish && mkdir -p ~/.config/fish && chsh -s /usr/bin/fish
COPY ../../../system-setup/config.fish ~/.config/fish/

# - Install starship and configure it
RUN curl -sS https://starship.rs/install.sh | sh -s -- -y
COPY ../../../utils/generate_starship_toml.py /tmp/generate_starship_toml.py
COPY ../../../utils/starship_template.toml /tmp/starship_template.toml
RUN python /tmp/generate_starship_toml.py $PROMPTHUE -o ~/.config/starship.toml --spacers 4 5 6 9

# - Entry by starting the nginx server
CMD ["nginx", "-g", "daemon off;"]
