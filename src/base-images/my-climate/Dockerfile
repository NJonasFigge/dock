
# === BASE IMAGE ===

# - Use the official lightweight Python image
FROM python:3.12-slim
WORKDIR /app


# === ARGUMENTS ===

# - PROMPTHUE defines which hue (0-360) the prompt shall have. Defaults to an ugly pink.
ARG PROMPTHUE="310"


# === SETUP TIMEZONE AND LOCALE ===

# - Set timezone to Berlin
RUN ln -sf /usr/share/zoneinfo/Europe/Berlin /etc/localtime

# - Add locale "de_DE.UTF-8" (e.g. for german weekdays)
RUN apt-get update && apt-get install -y locales \
    && sed -i '/de_DE.UTF-8/s/^# //g' /etc/locale.gen \
    && locale-gen


# === INSTALL BASIC PACKAGES CLIENT ===

# - Install curl and make
RUN apt-get update && \
    apt-get install -y bash curl make && \
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
RUN mkdir /root/.config/fish || true
COPY config.fish /root/.config/fish/


# === SETUP STARSHIP ===

# - Install starship the recommended way
RUN curl -sS https://starship.rs/install.sh | sh -s -- -y

# - Configure starship
COPY starship-utils ./starship-utils
