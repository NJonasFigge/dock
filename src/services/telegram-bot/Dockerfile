
# === BASE IMAGE ===

# - Use the my-climate base image
FROM my-climate:latest
WORKDIR /app


# === ARGUMENTS ===

# - PROMPTHUE defines which hue (0-360) the prompt shall have. Defaults to an ugly pink.
ARG PROMPTHUE="310"

# - REPO defines which git repo the telegram bot is in
ARG REPO=""
ENV REPO="$REPO"


# === ACTIVATE CUSTOM STARSHIP CONFIGURATION ===

# - Generate starship configuration with the given prompt hue inside the .config folder of the root user
RUN python starship-utils/generate_starship_toml.py $PROMPTHUE -o /root/.config/starship.toml --good-spacers


# === SET ENTRYPOINT ===

# - Deploy entrypoint script (which will pull the bot repo and then installs and runs it)
COPY entrypoint.sh .

# - Make entrypoint script runnable
RUN chmod +x entrypoint.sh

# - Set entrypoint script
ENTRYPOINT ["entrypoint.sh"]
