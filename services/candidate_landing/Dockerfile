# =============================================================================
# Candidate Landing Page
# Static site served by nginx with runtime environment variable substitution
# =============================================================================

FROM nginx:1.25-alpine

# Copy static files
COPY src/ /usr/share/nginx/html/

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port
EXPOSE 80

# Use entrypoint for runtime substitution
ENTRYPOINT ["/entrypoint.sh"]
