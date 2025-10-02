#! /bin/bash

# - Set parameters in environment
export VENV_DIR=/app/venv

# - Set to exit on error
set -e
trap 'echo "An error occurred in entrypoint script!"; bash' ERR

# - Clone branch to "bot" folder
echo "Cloning main branch of repo: $REPO"
cd /app
git clone -b "$BRANCH" "$REPO" bot

# - Install and run bot
cd bot
make install
make run
