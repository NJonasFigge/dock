
# === BASE IMAGE ===

# - Use the my-climate base image
FROM my-climate:latest
WORKDIR /app


# === ARGUMENTS ===

# - PROMPTHUE defines which hue (0-360) the prompt shall have. Defaults to an ugly pink.
ARG PROMPTHUE="310"

# - Generate starship configuration with the given prompt hue inside the .config folder of the root user
RUN python starship-utils/generate_starship_toml.py $PROMPTHUE -o /root/.config/starship.toml --good-spacers


# === INSTALL DEPENDENCIES ===

# - Install rsync and cron
RUN apt-get update && \
    apt-get install -y rsync cron && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get clean


# === DEPLOY CRON JOB ===

# - Add the rsync calls to the crontab file
COPY crontab /etc/cron.d/backup-maker-cron

# - Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/backup-maker-cron

# - Apply cron job
RUN crontab /etc/cron.d/backup-maker-cron


# === SET KEEPALIVE SCRIPT ===

# - Add the keepalive script to the image
COPY keepalive.sh /keepalive.sh

# - Make the keepalive script executable
RUN chmod +x /keepalive.sh

# - This will keep the container running
CMD ["/keepalive.sh"]
