#! /bin/bash

# - Clone branch to "bot" folder
echo "Cloning main branch of repo: $REPO"
cd /app || exit
git clone -b "$BRANCH" "$REPO" bot

# - Install and run bot
cd bot || exit
./project.mk install VENV_DIR=/venv
./project.mk run VENV_DIR=/venv
