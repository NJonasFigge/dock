#! /bin/bash

# - Set parameters in environment
export REPO="git@bitbucket.org:papierschiff-content/papsite.git"
export DEPLOY_TARGET=/usr/share/nginx/html
export VENV_DIR=/app/venv
export IS_LIVE=${IS_LIVE:-false}

# - Set to exit on error
set -e

# - Clean clone target
rm -rf /app/papsite

# - Find branch to use if BRANCH is "latest"
if [ "$BRANCH" = "latest" ]; then
  BRANCH=$(git ls-remote --heads "$REPO" | awk '{print $2}' | sed 's/refs\/heads\///' | sort -V | tail -n 1)
  export BRANCH
fi

# - Clone branch
echo "Cloning branch: $BRANCH"
cd /app
git clone -b "$BRANCH" "$REPO"

# - Deploy papsite from target
cd papsite
make deploy
