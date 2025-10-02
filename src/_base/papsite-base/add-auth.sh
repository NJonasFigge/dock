#! /bin/bash

# Check if argument is provided
if [ -z "$1" ]; then
  echo "Usage: $0 group1,group2,..."
  exit 1
fi

if [ "$1" = "www" ]; then
  echo "Argument is \"www\": Not injecting any auth files, serving publicly."
  exit 0
fi

# Backup Nginx config
cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.bak

# Split argument by commas
IFS=',' read -r -a groups <<< "$1"

# Temp combined htpasswd
COMBINED_HTPASSWD="/etc/nginx/auth/combined.htpasswd"
echo "" > "$COMBINED_HTPASSWD"  # empty the file

# Merge all group htpasswd files
for group in "${groups[@]}"; do
    if [ -f "/etc/nginx/auth/${group}.htpasswd" ]; then
        cat "/etc/nginx/auth/${group}.htpasswd" >> "$COMBINED_HTPASSWD"
    else
        echo "Warning: /etc/nginx/auth/${group}.htpasswd not found!"
    fi
done

# Update nginx.conf
sed -i "/location \/ {/a\\
  auth_basic \"Restricted\";\\
  auth_basic_user_file $COMBINED_HTPASSWD;" /etc/nginx/nginx.conf

echo "Authentication updated for groups: $1"
