#!/bin/sh

set -e

# Substitute environment variables in the Nginx config
envsubst < /etc/nginx/conf.d/default.conf.tpl > /etc/nginx/conf.d/default.conf

# Start Nginx in the foreground
nginx -g 'daemon off;'
