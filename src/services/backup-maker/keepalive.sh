#! /bin/bash

# This is a keepalive script to prevent this service from exiting.
# Its acual functionality is handled by cron jobs.
# See the Dockerfile for more information.

while true; do
    sleep 60
done
