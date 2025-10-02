#!/bin/bash

# Make banner to be injected
echo "<div style='background:yellow;padding:10px;text-align:center;'>Branch: $1 — Last updated: $(date)</div>" \
  > /usr/share/nginx/html/banner.html

# Let banner be included
sed -i '1i<!--#include virtual="banner.html" -->' /usr/share/nginx/html/index.html
