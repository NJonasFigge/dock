
# === BASE IMAGE ===

# - Use the official lightweight Python image
FROM python:3.12-slim


# === ARGUMENTS ===

# - PROMPTHUE defines which hue (0-360) the prompt shall have. Defaults to an ugly pink.
ARG PROMPTHUE="310"


# === SETUP TIMEZONE ===

# - Set timezone to Berlin
RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime


# === INSTALL BASIC PACKAGES CLIENT ===

# - Install curl and make
RUN apt-get update && \
    apt-get install -y curl make && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


# === SETUP SSH CLIENT ===

# - Install ssh client
RUN apt-get update && \
    apt-get install -y openssh-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# - Deploy ssh keys (for accessing private repos)
COPY dot-ssh /root/.ssh

# - Set permissions
RUN chmod 700 /root/.ssh && \
    chmod 600 /root/.ssh/id_ed25519 && \
    chmod 600 /root/.ssh/id_ed25519.pub

# - Add github and bitbucket to known ssh hosts
RUN ssh-keyscan github.com >> /root/.ssh/known_hosts && \
    ssh-keyscan bitbucket.org >> /root/.ssh/known_hosts


# === SETUP GIT ===

# - Install git
RUN apt-get update && \
    apt-get install -y git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


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
COPY starship-utils /app/starship-utils


# === SET WORKING DIRECTORY ===

# - Set working directory to /app
WORKDIR /app
