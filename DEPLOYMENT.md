# 🚀 Deployment Guide

## Quick Deploy Options (Free)

### Option 1: Railway (Recommended for Docker apps)
```bash
# 1. Push to GitHub
git add .
git commit -m "Ready for deployment"
git push origin main

# 2. Go to railway.app
# 3. Sign in with GitHub
# 4. New Project → Deploy from GitHub
# 5. Select this repository
# 6. Add environment variables (see below)
# 7. Deploy!
```

### Option 2: Render
```bash
# Backend (Web Service)
- Service Type: Web Service
- Environment: Docker
- Build Command: (auto-detected)
- Start Command: (auto-detected from Dockerfile)

# Frontend (Static Site)  
- Build Command: npm run build
- Publish Directory: dist
```

### Option 3: Fly.io
```bash
# Install flyctl
# Windows: iwr https://fly.io/install.ps1 -useb | iex
# Mac: curl -L https://fly.io/install.sh | sh

flyctl auth signup
flyctl launch  # Creates fly.toml
flyctl deploy
```

## 🔧 Environment Variables (Required)

Set these in your deployment platform:

```bash
# Google OAuth (Get from console.cloud.google.com)
GOOGLE_CLIENT_ID=your_actual_google_client_id
GOOGLE_CLIENT_SECRET=your_actual_google_client_secret

# Generate secure secret:
SECRET_KEY=run_node_-e_"console.log(require('crypto').randomBytes(64).toString('hex'))"

# Update URLs for production
GOOGLE_REDIRECT_URI=https://yourapp.railway.app/auth/google/callback
FRONTEND_URL=https://yourapp.railway.app
VITE_API_URL=https://yourapp-backend.railway.app
```

## 📝 Pre-deployment Checklist

1. ✅ Set up Google OAuth credentials for your domain
2. ✅ Update CORS settings in backend for production URL
3. ✅ Set all environment variables
4. ✅ Test locally with production-like config
5. ✅ Ensure database persists (volume mounts)

## 🎯 Recommended: Railway

**Why Railway?**
- Handles Docker Compose automatically  
- Built-in database options
- Automatic HTTPS
- $5/month free credits
- Easy environment variable management
- Connect custom domains

**Deploy Steps:**
1. railway.app → Login with GitHub
2. New Project → Deploy from GitHub repo
3. Select your repository
4. Railway auto-detects docker-compose.yml
5. Add environment variables in dashboard
6. Click Deploy

**Cost:** Free $5/month credits (plenty for development)

## 🌐 Alternative Combinations

### Frontend: Vercel + Backend: Railway
- Deploy React build to Vercel (free)
- Deploy FastAPI backend to Railway
- Best performance for static frontend

### Full Stack: Render
- Web Service for backend (Docker)
- Static Site for frontend
- Free PostgreSQL database

### Database Options
- **SQLite**: Works for small apps (file-based)
- **Railway PostgreSQL**: $5/month, managed
- **Render PostgreSQL**: Free tier available
- **PlanetScale**: Generous free tier

## 🔒 Production Security Notes

- Use strong SECRET_KEY (64+ characters)
- Enable HTTPS only in production
- Set secure cookie flags
- Validate CORS origins
- Use environment-specific Google OAuth URLs
