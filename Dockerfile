# Multi-stage build for Railway
FROM node:18-alpine as frontend-build

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Backend stage  
FROM python:3.11-slim

WORKDIR /app
RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*

# Copy backend code
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "import nltk; nltk.download('words', quiet=True)"

COPY backend/ ./
RUN mkdir -p /app/data

# Copy frontend build
COPY --from=frontend-build /app/frontend/dist ./static

# Install nginx to serve frontend
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*
COPY --from=frontend-build /app/frontend/dist /var/www/html

# Copy nginx config
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf

# Startup script
COPY <<EOF /start.sh
#!/bin/bash
nginx &
python main.py
EOF

RUN chmod +x /start.sh

EXPOSE 8000 80
CMD ["/start.sh"]
