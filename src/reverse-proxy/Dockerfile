
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

# - Entry by starting the nginx server
CMD ["nginx", "-g", "daemon off;"]
