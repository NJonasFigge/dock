
FROM python:3.12-slim
WORKDIR /app

COPY utils ./utils
RUN python utils/generate_starship_toml.py $PROMPTHUE -o /root/.config/starship.toml --good-spacers
