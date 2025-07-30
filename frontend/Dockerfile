# Frontend Dockerfile
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies with verbose logging
RUN echo "Installing dependencies..." && \
    npm install --verbose && \
    echo "Dependencies installed. Verifying vite:" && \
    npx vite --version

# Copy all source files
COPY . .

# Build the application with verbose logging
RUN echo "Starting build process..." && \
    npx vite build && \
    echo "Build completed. Contents of dist:" && \
    ls -la dist/

# Production stage with Nginx
FROM nginx:alpine

# Copy built assets from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx configuration template
COPY nginx.conf.template /etc/nginx/conf.d/default.conf.template

# Create startup script for Railway
RUN echo '#!/bin/sh' > /start.sh && \
    echo 'PORT=${PORT:-80}' >> /start.sh && \
    echo 'envsubst "\$PORT" < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf' >> /start.sh && \
    echo 'nginx -g "daemon off;"' >> /start.sh && \
    chmod +x /start.sh

# Expose port (Railway will override this)
EXPOSE 80

# Start with dynamic port
CMD ["/start.sh"]
