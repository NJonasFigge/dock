#!/bin/bash

### This script deploys the current BRANCH or a QUERY_BRANCH, if given by the user.

# - Set to exit on error
set -e

# - Output header to make it work as HTML output
echo "Content-type: text/plain"
echo ""

# - Set BRANCH to QUERY_STRING if given
if [[ -n "$QUERY_STRING" ]]; then
  BRANCH=$(echo "$QUERY_STRING" | cut -d= -f2)
  export BRANCH
fi

/app/deploy.sh

## - Pull desired branch
#cd /papsite-tmp
#git fetch origin
#git checkout "$BRANCH"
#git pull origin "$BRANCH"
#
## - Since pulling worked, set BRANCH globally now
#export BRANCH
#
## - Start deployment script
#./project.mk deploy DEPLOY_TARGET=/usr/share/nginx/html IS_LIVE="$IS_LIVE"
#echo "Deployed branch: $BRANCH"
