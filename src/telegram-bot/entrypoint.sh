#! /bin/bash

# - Set parameters in environment
export VENV_DIR=/app/venv

# - Set to exit on error
set -e

# - Clone branch to "bot" folder
echo "Cloning main branch of repo: $REPO"
cd /app
git clone -b "$BRANCH" "$REPO" bot

# - Install and run bot
cd bot
make install
make run
