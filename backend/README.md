# Wordle Backend

A FastAPI-based backend for a Wordle game with SQLite database integration.

## Files Structure

### Primary Files
- `main.py` - Main FastAPI application with full database integration
- `wordle_game.py` - Core game logic and database operations

### Support Files
- `main_old.py` - Original backend implementation (deprecated)
- `test_endpoints.py` - API endpoint tests
- `test_server.py` - Server functionality tests
- `debug_backend.py` - Debug utilities
- `wordle_stats.db` - SQLite database for game statistics

## Features

- **Session Management**: Persistent game sessions
- **Word Validation**: NLTK Brown Corpus for high-quality, contextual English words
- **Statistics Tracking**: Win rates, game history, and performance metrics
- **Database Storage**: SQLite database for persistent data
- **CORS Support**: Configured for frontend integration
- **Natural Language Processing**: Real-world vocabulary from published texts

## Running the Server

### Using VS Code Task
Run the "Start Backend Server" task in VS Code.

### Manual Start
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /start_game` - Start a new game session
- `POST /guess` - Submit a word guess
- `GET /stats` - Get user statistics
- `GET /stats/{session_id}` - Get specific session stats

## Database Schema

The SQLite database tracks:
- Game sessions and outcomes
- User statistics and performance
- Word validation and game history
