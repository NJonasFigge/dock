
# === BASE IMAGE ===

# - Use the my-climate base image
FROM my-climate:latest


# === BASE IMAGE ===

# - Use the my-climate base image
FROM my-climate:latest


# === ARGUMENTS ===

# - PROMPTHUE defines which hue (0-360) the prompt shall have. Defaults to an ugly pink.
ARG PROMPTHUE="310"


# === ACTIVATE CUSTOM STARSHIP CONFIGURATION ===

# - Generate starship configuration with the given prompt hue inside the .config folder of the root user
RUN python utils/generate_starship_toml.py $PROMPTHUE -o /root/.config/starship.toml --good-spacers


# === SET COMMAND ===

# - Open shell
CMD [ "fish" ]
