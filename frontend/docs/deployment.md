# Deployment Documentation

This document describes how to build, deploy, and configure the Wordle game frontend for different environments.

## 🚀 Build Process

### Development Build
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Development server runs on http://localhost:5173
```

### Production Build
```bash
# Create optimized production build
npm run build

# Preview production build locally
npm run preview

# Production preview runs on http://localhost:4173
```

### Build Configuration
```javascript
// vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    sourcemap: process.env.NODE_ENV !== 'production',
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          ui: ['@headlessui/react']
        }
      }
    }
  },
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  },
  preview: {
    port: 4173,
    host: true
  }
})
```

## 🐳 Docker Deployment

### Multi-stage Dockerfile
```dockerfile
# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx Configuration
```nginx
# nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log notice;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    keepalive_timeout 65;
    gzip on;

    # Frontend server
    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # Enable gzip compression
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_comp_level 6;
        gzip_types
            text/plain
            text/css
            text/xml
            text/javascript
            application/json
            application/javascript
            application/xml+rss
            application/atom+xml
            image/svg+xml;

        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Handle client-side routing
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Proxy API requests to backend
        location /api {
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

### Docker Compose Integration
```yaml
# docker-compose.yml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: wordle-frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - NODE_ENV=production
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  backend:
    build: ./backend
    container_name: wordle-backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_PATH=/app/data/wordle_stats.db
    volumes:
      - wordle_data:/app/data
    restart: unless-stopped

volumes:
  wordle_data:
```

## 🌐 Environment Configuration

### Environment Variables
```javascript
// src/utils/config.js
const config = {
  // API Configuration
  API_BASE_URL: process.env.REACT_APP_API_BASE_URL || 
    (process.env.NODE_ENV === 'production' 
      ? 'https://your-backend-domain.com' 
      : 'http://localhost:8000'),

  // Authentication
  GOOGLE_CLIENT_ID: process.env.REACT_APP_GOOGLE_CLIENT_ID,
  
  // Features
  ENABLE_GOOGLE_AUTH: process.env.REACT_APP_ENABLE_GOOGLE_AUTH === 'true',
  ENABLE_MULTIPLAYER: process.env.REACT_APP_ENABLE_MULTIPLAYER === 'true',
  
  // Analytics
  GOOGLE_ANALYTICS_ID: process.env.REACT_APP_GA_ID,
  
  // App Configuration
  APP_NAME: process.env.REACT_APP_NAME || 'Wordle Game',
  APP_VERSION: process.env.REACT_APP_VERSION || '1.0.0',
  
  // Debug
  DEBUG: process.env.NODE_ENV === 'development'
};

export default config;
```

### Environment Files
```bash
# .env.development
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_ENABLE_GOOGLE_AUTH=true
REACT_APP_ENABLE_MULTIPLAYER=true
REACT_APP_GOOGLE_CLIENT_ID=your-dev-client-id

# .env.production
REACT_APP_API_BASE_URL=https://api.yourapp.com
REACT_APP_ENABLE_GOOGLE_AUTH=true
REACT_APP_ENABLE_MULTIPLAYER=true
REACT_APP_GOOGLE_CLIENT_ID=your-prod-client-id
REACT_APP_GA_ID=your-analytics-id

# .env.local (not committed to git)
REACT_APP_GOOGLE_CLIENT_ID=your-actual-client-id
```

## ☁️ Cloud Deployment

### Vercel Deployment
```json
// vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "https://your-backend-domain.com/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ],
  "env": {
    "REACT_APP_API_BASE_URL": "https://your-backend-domain.com"
  }
}
```

### Netlify Deployment
```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = "dist"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/api/*"
  to = "https://your-backend-domain.com/api/:splat"
  status = 200

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[context.production]
  environment = { REACT_APP_API_BASE_URL = "https://your-backend-domain.com" }

[context.deploy-preview]
  environment = { REACT_APP_API_BASE_URL = "https://staging-backend.com" }
```

### Railway Deployment
```dockerfile
# Dockerfile.railway
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Use environment variable for backend URL
ENV BACKEND_URL=http://backend:8000

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```nginx
# nginx.conf.template
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass ${BACKEND_URL};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔧 Build Optimization

### Bundle Analysis
```bash
# Install bundle analyzer
npm install --save-dev rollup-plugin-visualizer

# Add to vite.config.js
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    react(),
    visualizer({
      filename: 'dist/stats.html',
      open: true
    })
  ]
});

# Generate bundle analysis
npm run build
```

### Code Splitting
```javascript
// Lazy load components
import { lazy, Suspense } from 'react';

const PracticeGame = lazy(() => import('./pages/PracticeGame'));
const MultiplayerGame = lazy(() => import('./pages/MultiplayerGame'));
const StatsScreen = lazy(() => import('./pages/StatsScreen'));

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/practice" element={
          <Suspense fallback={<LoadingSpinner />}>
            <PracticeGame />
          </Suspense>
        } />
        <Route path="/multiplayer" element={
          <Suspense fallback={<LoadingSpinner />}>
            <MultiplayerGame />
          </Suspense>
        } />
      </Routes>
    </Router>
  );
};
```

### Asset Optimization
```javascript
// vite.config.js optimization
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        // Create separate chunks for better caching
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          utils: ['axios', 'date-fns']
        }
      }
    },
    // Enable source maps for production debugging
    sourcemap: process.env.GENERATE_SOURCEMAP !== 'false',
    // Minify assets
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: process.env.NODE_ENV === 'production',
        drop_debugger: true
      }
    }
  }
});
```

## 📊 Performance Monitoring

### Web Vitals
```javascript
// src/utils/analytics.js
import { getCLS, getFID, getFCP, getLCP, getTTFB } from 'web-vitals';

const sendToAnalytics = (metric) => {
  // Send to your analytics service
  if (window.gtag) {
    window.gtag('event', metric.name, {
      value: Math.round(metric.value),
      event_category: 'Web Vitals',
      event_label: metric.id,
      non_interaction: true
    });
  }
};

// Measure all Web Vitals
getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getFCP(sendToAnalytics);
getLCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

### Error Tracking
```javascript
// Error boundary for production error tracking
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error to monitoring service
    if (process.env.NODE_ENV === 'production') {
      console.error('Application error:', error, errorInfo);
      // Send to error tracking service (Sentry, LogRocket, etc.)
    }
  }

  render() {
    if (this.state.hasError) {
      return <ErrorPage />;
    }

    return this.props.children;
  }
}
```

## 🚦 Deployment Checklist

### Pre-deployment
- [ ] Run `npm run build` successfully
- [ ] Test production build with `npm run preview`
- [ ] Verify all environment variables are set
- [ ] Check bundle size and performance
- [ ] Test on different devices and browsers
- [ ] Verify API endpoints are accessible
- [ ] Check SSL certificates for HTTPS

### Deployment
- [ ] Deploy to staging environment
- [ ] Run smoke tests on staging
- [ ] Verify authentication flows
- [ ] Test game functionality
- [ ] Check error tracking is working
- [ ] Verify analytics integration
- [ ] Deploy to production

### Post-deployment
- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Verify all features working
- [ ] Monitor server resources
- [ ] Update DNS if needed
- [ ] Notify team of deployment
