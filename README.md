# Wordle Game

A full-stack Wordle game implementation with React frontend and FastAPI backend.

## Project Structure

```
├── backend/
│   ├── main.py              # Main FastAPI server with SQLite database
│   ├── main_old.py          # Deprecated - old version without database
│   ├── wordle_game.py       # Original game logic functions
│   ├── wordle_stats.db      # SQLite database (created automatically)
│   └── test_*.py           # Testing utilities
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── App.css          # Main styling
│   │   ├── Stats.jsx        # Statistics modal component
│   │   └── Stats.css        # Statistics styling
│   └── package.json
└── .vscode/
    └── tasks.json           # VS Code tasks for running servers
```

## Features

### Game Features
- Multiple difficulty levels (Easy: 4 letters, Medium: 5 letters, Hard: 6 letters)
- Word validation - only valid English words are accepted
- Real-time color feedback (Green: correct, Yellow: wrong position, Red: not in word)
- 6 attempts per game
- Dynamic grid sizing based on difficulty

### Statistics Features
- Persistent SQLite database storage
- Comprehensive statistics tracking:
  - Total games, wins, losses, win rate
  - Current streak and max streak
  - Average guesses for won games
  - Guess distribution visualization
  - Statistics by difficulty level
- Game history with last 20 games
- Reset statistics functionality

## Running the Game

### Backend Server
```bash
cd backend
python main.py
```
Server runs on http://localhost:8000

### Frontend Server
```bash
cd frontend
npm run dev
```
Frontend runs on http://localhost:5173

### Using VS Code Tasks
- Open Command Palette (`Ctrl+Shift+P`)
- Type "Tasks: Run Task"
- Select "Start Backend Server"
- Manually start frontend with `npm run dev`

## API Endpoints

- `POST /new-game/{difficulty}` - Start a new game
- `POST /guess/{session_id}` - Submit a guess
- `GET /stats` - Get comprehensive statistics
- `GET /history` - Get recent game history
- `POST /reset-stats` - Reset all statistics
- `POST /validate-word` - Check if a word is valid

## Word Validation

The game includes comprehensive word lists for each difficulty level:
- **4-letter words**: 100+ valid words
- **5-letter words**: 300+ valid words  
- **6-letter words**: 300+ valid words

Only valid English words are accepted as guesses.

## Database Schema

### Games Table
- `id`: Auto-increment primary key
- `word`: The target word
- `difficulty`: easy/medium/hard
- `guesses`: Number of guesses taken
- `won`: Boolean win/loss status
- `timestamp`: When the game was completed
- `session_id`: Unique session identifier

### User Stats Table
- `current_streak`: Current win streak
- `max_streak`: Maximum win streak achieved
- `last_updated`: Last update timestamp

## Development Notes

- `main.py` is the current active backend file
- `main_old.py` contains the deprecated version without database features
- Database file `wordle_stats.db` is created automatically on first run
- All statistics persist between server restarts
