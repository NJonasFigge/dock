#!/bin/bash

# - Set to exit on error
set -e
trap 'echo "An error occurred in entrypoint.sh!"; bash' ERR

# - Deploy the correct version of papsite
/app/deploy.sh

# - Start the nginx server
nginx -g 'daemon off;'
