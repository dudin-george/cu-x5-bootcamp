#!/bin/sh
set -e

# Replace placeholder with environment variable
# Default to dev bot if not set
TELEGRAM_BOT_URL="${TELEGRAM_BOT_URL:-https://t.me/X5Team_DEV_InternBot}"

echo "Configuring Telegram Bot URL: $TELEGRAM_BOT_URL"

# Replace in all HTML files
find /usr/share/nginx/html -name "*.html" -exec sed -i "s|%%TELEGRAM_BOT_URL%%|${TELEGRAM_BOT_URL}|g" {} \;

# Start nginx
exec nginx -g "daemon off;"

