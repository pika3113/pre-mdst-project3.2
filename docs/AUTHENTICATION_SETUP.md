# Environment Configuration for Account System

## Required Environment Variables

### Backend (.env file in /backend directory)
```
# Google OAuth Configuration
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/google/callback

# JWT Secret (generate a secure random string)
SECRET_KEY=your_very_secure_jwt_secret_key_here

# Database Path (optional, defaults to wordle_stats.db)
DATABASE_PATH=wordle_stats.db
```

## Setup Instructions

### 1. Google OAuth Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google+ API and Google OAuth2 API
4. Go to "Credentials" -> "Create Credentials" -> "OAuth 2.0 Client ID"
5. Choose "Web application"
6. Add authorized redirect URIs:
   - `http://localhost:3000/auth/google/callback` (for development)
   - `http://your-domain.com/auth/google/callback` (for production)
7. Copy the Client ID and Client Secret to your .env file

### 2. JWT Secret Generation
Generate a secure random string for JWT signing:
```bash
# In Node.js
node -e "console.log(require('crypto').randomBytes(64).toString('hex'))"

# Or use online generator (but less secure)
```

### 3. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 4. Run the Application
```bash
# Backend
cd backend
python main.py

# Frontend (in another terminal)
cd frontend
npm run dev
```

## Features Implemented

### Backend Features
- ✅ User registration with email/password
- ✅ User login with JWT authentication 
- ✅ Google OAuth integration
- ✅ Password hashing with bcrypt
- ✅ JWT token management
- ✅ User profile with Google profile pictures
- ✅ Database schema with user tables
- ✅ Session management
- ✅ Account linking (link Google to existing email account)

### Frontend Features
- ✅ Modern authentication modal
- ✅ Google OAuth "Sign in with Google" button
- ✅ User registration and login forms
- ✅ User profile display in header
- ✅ Google OAuth callback handling
- ✅ JWT token storage and management
- ✅ Automatic authentication on page load
- ✅ Logout functionality
- ✅ Responsive design

### Security Features
- ✅ Password hashing (bcrypt)
- ✅ JWT token authentication
- ✅ Google OAuth 2.0 integration
- ✅ SQL injection protection (parameterized queries)
- ✅ Input validation
- ✅ CORS configuration
- ✅ Authentication middleware

## Next Steps
After setting up the basic authentication, you can:
1. Link games to user accounts (user_id foreign key already added)
2. Add friends system
3. Implement multiplayer features
4. Add user statistics per account
5. Add profile management
6. Add password reset functionality

## Database Schema
The system automatically creates these tables:
- `users` - User account information
- `user_sessions` - Session management
- `games` - Game records (now with user_id)
- `user_stats` - User statistics (now with user_id)
