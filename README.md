  # Wordle Game

A modern full-stack Wordle game implementation with React frontend and FastAPI backend, featuring comprehensive word validation and elegant UI design.

## Project Structure

`### Development Notes

### File Organization
- `main.py`: Current active backend with NLTK Brown Corpus integration
- `main_old.py`: Legacy version without database features
- `test_validation.py`: NLTK Brown Corpus word validation testing utilities
- Database files are created automatically on first run

### Technical Stack
- **Backend**: FastAPI with SQLite database
- **Frontend**: React with modern CSS animations
- **Word Processing**: NLTK Brown Corpus with SSL certificate handling
- **Validation**: Cached word sets for optimal performance
- **Containerization**: Docker with multi-stage builds and nginx proxy
- **Deployment**: Docker Compose orchestration with volume persistence
- **Development**: Hot reload support with development containers
│   ├── main.py              # Main FastAPI server with NLTK Brown Corpus validation
│   ├── main_old.py          # Deprecated - old version without database
│   ├── wordle_game.py       # Original game logic functions
│   ├── wordle_stats.db      # SQLite database (created automatically)
│   ├── test_validation.py   # Word validation testing utilities
│   └── test_*.py           # Additional testing utilities
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component with modern UI
│   │   ├── App.css          # Modern gradient styling with animations
│   │   ├── Stats.jsx        # Animated side panel statistics
│   │   └── Stats.css        # Side panel styling with smooth transitions
│   └── package.json
├── start_backend.bat        # Automated backend startup
├── start_wordle_game.bat    # Automated full game startup
└── .vscode/
    └── tasks.json           # VS Code tasks for running servers
```

## Features

### Game Features
- **Multiple difficulty levels**: Easy (4 letters), Medium (5 letters), Hard (6 letters)
- **NLTK Brown Corpus word validation**: High-quality English words from real publications
  - Contextual words from books, newspapers, and academic texts
  - More realistic vocabulary than dictionary-only sources
  - Common usage patterns for better gameplay experience
- **Real-time feedback**: Green (correct), Yellow (wrong position), Red (not in word)
- **Dynamic grid sizing**: Adapts to difficulty level
- **Modern gradient UI**: Purple theme with glass-morphism effects
- **Smooth animations**: Transitions and hover effects throughout

### Statistics Features
- **Persistent SQLite database**: All data saved between sessions
- **Animated side panel**: Slides in/out with smooth cubic-bezier transitions
- **Comprehensive tracking**:
  - Total games, wins, losses, win rate
  - Current streak and maximum streak
  - Average guesses for won games
  - Guess distribution visualization
  - Detailed statistics by difficulty level
- **Game history**: Last 20 games with full details
- **Reset functionality**: Clear all statistics when needed

## Running the Game

### 🐳 Docker (Recommended)

#### Quick Start with Docker
```bash
# Start the entire application
start_docker.bat

# Or manually with docker-compose
docker-compose up --build
```

**Ports:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000

#### Development with Docker
```bash
# For development with hot reload
docker-compose -f docker-compose.dev.yml up --build
```

#### Docker Commands
```bash
# Stop containers
stop_docker.bat
# OR
docker-compose down

# View logs
docker-compose logs -f

# Rebuild containers
docker-compose up --build

# Remove everything (including database)
docker-compose down -v
```

### Manual Setup (Alternative)

#### Quick Start (Recommended)
```bash
# Start both backend and frontend automatically
start_wordle_game.bat
```
This will launch both servers and open the game in your browser.

#### Manual Startup

##### Backend Server
```bash
cd backend
python main.py
# OR use the batch file
start_backend.bat
```
Server runs on http://localhost:8000

##### Frontend Server
```bash
cd frontend
npm install  # First time only
npm run dev
```
Frontend runs on http://localhost:5173

### Using VS Code Tasks
- Open Command Palette (`Ctrl+Shift+P`)
- Type "Tasks: Run Task"
- Select "Start Backend Server"
- Manually start frontend with `npm run dev`

## API Endpoints

- `POST /new-game/{difficulty}` - Start a new game (returns session_id)
- `POST /guess/{session_id}` - Submit a guess for validation
- `GET /stats` - Get comprehensive game statistics
- `GET /history` - Get recent game history (last 20 games)
- `POST /reset-stats` - Reset all statistics and history
- `POST /validate-word` - Check if a word is valid (testing endpoint)

## Advanced Word Validation System

The game features a sophisticated NLTK Brown Corpus-powered word validation system:

### Word Library
- **Source**: NLTK Brown Corpus - real English text from publications
- **Quality**: Words from actual books, newspapers, and academic texts
- **Context**: Natural language usage patterns for authentic vocabulary
- **Filtering**: Only alphabetic words of appropriate lengths (4, 5, 6 letters)

### Technical Implementation
- **Brown Corpus integration**: Words extracted from real published text
- **Cached validation**: Words loaded once at startup for instant lookup
- **Fallback system**: Hardcoded word lists if NLTK fails to load
- **SSL handling**: Automatic certificate management for NLTK downloads
- **Performance optimized**: Set-based lookups for O(1) validation speed

### Word Quality
- All words sourced from real published English text
- Natural vocabulary reflecting actual language usage
- No artificial dictionary-only obscure terms
- Better player experience with familiar words
- Examples: ABOUT, WHICH, THEIR, WOULD, COULD

## Database Schema

### Games Table
- `id`: Auto-increment primary key
- `word`: The target word for the game
- `difficulty`: Game difficulty (easy/medium/hard)
- `guesses`: Number of guesses taken to complete
- `won`: Boolean indicating win/loss status
- `timestamp`: Game completion timestamp
- `session_id`: Unique session identifier for tracking

### User Stats Table
- `id`: Primary key (always 1 for single user)
- `total_games`: Total number of games played
- `total_wins`: Total number of games won
- `current_streak`: Current consecutive wins
- `max_streak`: Maximum consecutive wins achieved
- `last_updated`: Last statistics update timestamp

## UI/UX Features

### Modern Design
- **Gradient theme**: Purple gradient backgrounds with smooth transitions
- **Glass-morphism**: Semi-transparent panels with backdrop blur effects
- **Inter font**: Modern, clean typography throughout
- **Responsive design**: Adapts to different screen sizes

### Animations
- **Side panel statistics**: Smooth slide-in/out with cubic-bezier easing
- **Button interactions**: Hover effects and state transitions
- **Grid animations**: Subtle cell highlighting and feedback
- **Staggered loading**: Sequential animation of statistics elements

### User Experience
- **Keyboard support**: Full keyboard navigation and input
- **Visual feedback**: Immediate response to all user actions
- **Error handling**: Clear messaging for invalid inputs
- **Persistent state**: Game progress maintained during session

## Development Notes

### File Organization
- `main.py`: Current active backend with NLTK integration
- `main_old.py`: Legacy version without database features
- `test_validation.py`: NLTK word validation testing utilities
- Database files are created automatically on first run

### Technical Stack
- **Backend**: FastAPI with SQLite database
- **Frontend**: React with modern CSS animations
- **Word Processing**: NLTK corpus with SSL certificate handling
- **Validation**: Cached word sets for optimal performance
- **Containerization**: Docker with multi-stage builds and nginx proxy
- **Deployment**: Docker Compose orchestration with volume persistence
- **Development**: Hot reload support with development containers

### Performance Optimizations
- Word lists generated once at server startup
- Cached validation sets for instant word lookup
- Efficient database queries with proper indexing
- Minimal API calls with session-based state management
