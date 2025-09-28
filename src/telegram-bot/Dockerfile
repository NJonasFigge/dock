
FROM python:3.12-slim
WORKDIR /app

# === LAYERS ===

# - REPO defines which git repo the telegram bot is in
ARG REPO=""
ENV REPO="$REPO"

# - Deploy entrypoint script (which will deploy the site on runtime)
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# - Set entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
