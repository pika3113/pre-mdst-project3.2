# Frontend Dockerfile
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy all source files
COPY . .

# Build the application
RUN npm run build

# Production stage with Nginx
FROM nginx:alpine

# Install gettext for envsubst
RUN apk add --no-cache gettext

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Create nginx config template that uses Railway's PORT
RUN echo 'server {' > /etc/nginx/conf.d/default.conf.template && \
    echo '    listen $PORT;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '    server_name localhost;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '    root /usr/share/nginx/html;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '    index index.html;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '    location / {' >> /etc/nginx/conf.d/default.conf.template && \
    echo '        try_files $uri $uri/ /index.html;' >> /etc/nginx/conf.d/default.conf.template && \
    echo '    }' >> /etc/nginx/conf.d/default.conf.template && \
    echo '}' >> /etc/nginx/conf.d/default.conf.template

# Remove default nginx config
RUN rm -f /etc/nginx/conf.d/default.conf

# Create startup script that substitutes PORT
RUN echo '#!/bin/sh' > /docker-entrypoint.sh && \
    echo 'export PORT=${PORT:-80}' >> /docker-entrypoint.sh && \
    echo 'envsubst "\$PORT" < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf' >> /docker-entrypoint.sh && \
    echo 'nginx -g "daemon off;"' >> /docker-entrypoint.sh && \
    chmod +x /docker-entrypoint.sh

# Expose port (Railway will override this)
EXPOSE 80

# Use the startup script
CMD ["/docker-entrypoint.sh"]