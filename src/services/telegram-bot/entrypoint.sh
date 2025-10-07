#! /bin/bash

# - Set parameters in environment
export VENV_DIR=/app/venv

# - Set to exit on error
set -e
trap 'echo "An error occurred in entrypoint script!"' ERR

# - Clone branch to "bot" folder
echo "Cloning main branch of repo: $REPO"
cd /app
git clone "$REPO" bot

# - Install and run bot
cd bot
make install
echo "Bot setup complete. Activate the bot by uncommenting the 'make run' in 'entrypoint.sh' (and removing this text)."
# make run
