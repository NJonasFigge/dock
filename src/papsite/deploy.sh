#! /bin/bash

REPO="git@bitbucket.org:papierschiff-content/papsite.git"

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
cd /app || exit
git clone -b "$BRANCH" "$REPO"

# - Deploy papsite from target
cd papsite || exit
./project.mk deploy DEPLOY_TARGET=/usr/share/nginx/html IS_LIVE="$IS_LIVE" VENV_DIR=/venv
