#!/bin/bash

/app/deploy.sh

# - Start the nginx server
nginx -g 'daemon off;'
