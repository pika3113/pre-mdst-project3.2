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

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
