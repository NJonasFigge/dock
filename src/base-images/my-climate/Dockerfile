
# === BASE IMAGE ===

# - Use the official lightweight Python image
FROM python:3.12-slim


# === ARGUMENTS ===

# - PROMPTHUE defines which hue (0-360) the prompt shall have. Defaults to an ugly pink.
ARG PROMPTHUE="310"


# === SETUP TIMEZONE ===

# - Set timezone to Berlin
RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime


# === SETUP SSH CLIENT ===

# - Install ssh client
RUN apt-get update && \
    apt-get install -y openssh-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# === SETUP GIT ===

# - Install git
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# - Deploy ssh keys (for accessing private repos)
COPY dot-ssh /root/.ssh

# - Add github and bitbucket to known ssh hosts
RUN mkdir -p /root/.ssh && \
    ssh-keyscan github.com >> /root/.ssh/known_hosts && \
    ssh-keyscan bitbucket.org >> /root/.ssh/known_hosts


# === SETUP FISH ===

# - Install fish
RUN apt-get update && \
    apt-get install -y fish && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# - Deploy fish configuration
WORKDIR /root/.config
RUN mkdir fish || true
COPY config.fish fish/


# === SETUP STARSHIP ===

# - Install starship the recommended way
RUN curl -sS https://starship.rs/install.sh | sh -s -- -y

# - Configure starship
COPY starship-utils /app/


# === SET WORKING DIRECTORY ===

# - Set working directory to /app
WORKDIR /app
