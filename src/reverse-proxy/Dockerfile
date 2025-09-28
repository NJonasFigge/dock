
FROM nginx:alpine

# === LAYERS ===

# - Install bash
RUN apk add --no-cache bash

# - Deploy nginx configuration file
COPY nginx.conf /etc/nginx/nginx.conf

# - Entry by starting the nginx server
CMD ["nginx", "-g", "daemon off;"]
