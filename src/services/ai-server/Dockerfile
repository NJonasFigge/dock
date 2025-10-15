
# === BASE IMAGE ===

# - Use the my-climate base image
FROM my-climate:latest
WORKDIR /app


# === ARGUMENTS ===

# - PROMPTHUE defines which hue (0-360) the prompt shall have. Defaults to an ugly pink.
ARG PROMPTHUE="310"


# === ACTIVATE CUSTOM STARSHIP CONFIGURATION ===

# - Generate starship configuration with the given prompt hue inside the .config folder of the root user
RUN python starship-utils/generate_starship_toml.py $PROMPTHUE -o /root/.config/starship.toml --good-spacers


# === EXTEND ABOUT FILE ===

# - Deploy about file extension
COPY about-this-service.md /tmp/about-this-service-extension.md

# - Append to about file
RUN cat /tmp/about-this-service-extension.md >> /app/about-this-service.md && \
    rm /tmp/about-this-service-extension.md


# === SET COMMAND ===

# - Open shell
CMD ["fish"]
