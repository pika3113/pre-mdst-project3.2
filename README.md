  # WordGames Hub

A beautiful collection of word-based games including Wordle, Morphle, and Hangman. Play solo or compete with friends using Google sign-in to track your progress and achievements.

## 🎮 Games Available

### Wordle
Classic word-guessing game with three difficulty levels:
- **Easy**: 4-letter words
- **Medium**: 5-letter words  
- **Hard**: 6-letter words

### Morphle
Transform one word into another by changing one letter at a time.

### Hangman
Traditional word-guessing game with hints available.

## ✨ Features

- **Multiple Games**: Three different word games in one app
- **User Accounts**: Sign in with Google to save your progress
- **Statistics Tracking**: See your wins, streaks, and improvement over time
- **Beautiful Design**: Modern purple theme with smooth animations
- **Smart Word Lists**: Uses real English words from published texts
- **Responsive**: Works great on desktop and mobile
```

## 🚀 Quick Start

### Using Docker (Easiest)
```bash
# Start the app
docker-compose up --build

# Stop the app
docker-compose down
```
Then visit http://localhost:3000

### Manual Setup
```bash
# Start everything at once
start_wordle_game.bat
```

## 📊 Your Statistics

Track your gaming progress with detailed statistics:
- **Win Rate**: See how you're improving over time
- **Streaks**: Current and best winning streaks
- **Game History**: Review your recent games
- **Difficulty Breakdown**: Stats for each difficulty level
- **Average Guesses**: See how efficiently you solve puzzles

## � For Developers

### Tech Stack
- **Frontend**: React with modern CSS and animations
- **Backend**: FastAPI (Python) with SQLite database
- **Authentication**: Google OAuth integration
- **Word Processing**: NLTK corpus for high-quality word validation
- **Deployment**: Docker containers with nginx proxy

### Key Technical Features
- Real-time game state management
- Cached word validation for fast gameplay
- Responsive design with smooth animations
- RESTful API with comprehensive endpoints
- Persistent user data and statistics

### Project Structure
```
backend/
├── main.py              # Main server with game logic
├── models/              # Game data models
├── services/            # Game logic and authentication
├── api/                 # API endpoints
└── core/                # Database and configuration

frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── pages/           # Game screens and menus
│   ├── services/        # API communication
│   └── hooks/           # Custom React hooks
└── public/              # Static assets and icons
```

### Development Commands
```bash
# View logs
docker-compose logs -f

# Rebuild containers
docker-compose up --build

# Development mode with hot reload
docker-compose -f docker-compose.dev.yml up

# Reset database
docker-compose down -v
```

### Environment Setup
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Database: SQLite (auto-created)

## 🎯 Contributing

This project welcomes contributions! Key areas for improvement:
- New game modes and variations
- UI/UX enhancements
- Performance optimizations
- Additional authentication providers
- Mobile app version
