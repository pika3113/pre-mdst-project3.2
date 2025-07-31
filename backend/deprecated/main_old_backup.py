from fastapi import FastAPI, HTTPException, Depends, status, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import string
import sqlite3
from datetime import datetime, timedelta
from typing import Optional
import os
import nltk
from auth import AuthManager
from auth_models import UserCreate, UserLogin, UserResponse, Token, GoogleAuthRequest, GoogleAuthResponse
from google_auth import GoogleOAuthService
from nltk.corpus import words
import ssl
import pytz

# Download NLTK data if not already present
try:
    # Try to create unverified HTTPS context for NLTK downloads
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context
    
    # Download words corpus if not present
    nltk.data.find('corpora/words')
except LookupError:
    nltk.download('words', quiet=True)

app = FastAPI()

# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:5174", 
        "http://localhost:3000",
        "https://frontend-production-3bb7.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],   
)

# Generate word lists dynamically from NLTK corpus
def generate_word_lists():
    """Generate word lists for each difficulty level from NLTK corpus"""
    try:
        # Get all English words from NLTK
        english_words = set(word.upper() for word in words.words() if word.isalpha())
        
        # Filter words by length
        word_lists = {4: [], 5: [], 6: []}
        
        for word in english_words:
            word_len = len(word)
            if word_len in [4, 5, 6]:
                # Just filter by length, no additional restrictions for more variety
                word_lists[word_len].append(word)
        
        # Limit to reasonable sizes and sort for consistency
        for length in word_lists:
            word_lists[length] = sorted(word_lists[length])[:3000]  # Increased to 3000 words per difficulty
            
        return word_lists
    except Exception as e:
        print(f"Error generating word lists from NLTK: {e}")
        # Fallback to basic word lists if NLTK fails
        return {
            4: ["WORD", "GAME", "PLAY", "BEST", "LOVE", "LIFE", "TIME", "GOOD", "MAKE", "WORK", "HELL", "BALL", "CALL", "FALL"],
            5: ["WORDS", "GAMES", "PLAYS", "LOVED", "LIVES", "TIMES", "GOODS", "MAKES", "WORKS", "STUDY", "HELLO", "BALLS", "CALLS", "FALLS"],
            6: ["WORDLE", "GAMING", "PLAYER", "LOVING", "LIVING", "TIMING", "MAKING", "WORKED", "STUDIED", "BETTER", "HELLOS", "CALLED", "FALLEN", "BALLED"]
        }

# Generate word lists on startup
WORD_LISTS = generate_word_lists()

# Cache all valid words for efficient validation
ALL_VALID_WORDS = {}
try:
    all_english_words = set(word.upper() for word in words.words() if word.isalpha())
    for word in all_english_words:
        word_len = len(word)
        if word_len in [4, 5, 6]:
            if word_len not in ALL_VALID_WORDS:
                ALL_VALID_WORDS[word_len] = set()
            ALL_VALID_WORDS[word_len].add(word)
except:
    # Fallback if NLTK fails
    ALL_VALID_WORDS = {
        4: set(WORD_LISTS[4]),
        5: set(WORD_LISTS[5]),
        6: set(WORD_LISTS[6])
    }

def is_valid_word(word: str, word_length: int) -> bool:
    """Check if a word is valid using cached word set"""
    word = word.upper()
    return word in ALL_VALID_WORDS.get(word_length, set())

difficulty_levels = {
    "easy": 4,
    "medium": 5,
    "hard": 6
}

# Game state storage
game_sessions = {}

# Timezone helper function
def get_sgt_time():
    """Get current time in Singapore timezone"""
    sgt = pytz.timezone('Asia/Singapore')
    return datetime.now(sgt)

# Database setup
DATABASE_PATH = os.getenv("DATABASE_PATH", "wordle_stats.db")

def init_database():
    """Initialize SQLite database with required tables"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Create games table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            guesses INTEGER NOT NULL,
            won BOOLEAN NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            session_id TEXT
        )
    ''')
    
    # Create user_stats table for additional stats
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY,
            total_games INTEGER DEFAULT 0,
            total_wins INTEGER DEFAULT 0,
            current_streak INTEGER DEFAULT 0,
            max_streak INTEGER DEFAULT 0,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert initial stats row if it doesn't exist
    cursor.execute('INSERT OR IGNORE INTO user_stats (id) VALUES (1)')
    
    conn.commit()
    conn.close()

def migrate_timestamps_to_sgt():
    """Migrate existing timestamps to SGT if they are in UTC format"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if there are any games with timestamps that need migration
        cursor.execute('SELECT COUNT(*) FROM games WHERE timestamp IS NOT NULL')
        count = cursor.fetchone()[0]
        
        if count > 0:
            print(f"Found {count} games with timestamps. Checking if migration is needed...")
            
            # For now, log this. In production, might want to
            # convert UTC timestamps to SGT,,
            # the new games will use the correct SGT timezone.
            print("New games will be saved with SGT timezone.")
        
    except sqlite3.Error as e:
        print(f"Error during timestamp migration: {e}")
    finally:
        conn.close()

# Initialize database on startup
init_database()
migrate_timestamps_to_sgt()

# Initialize authentication manager
auth_manager = AuthManager(DATABASE_PATH)

# Initialize Google OAuth service
google_oauth = GoogleOAuthService()

class GuessRequest(BaseModel):
    guess: str

class NewGameRequest(BaseModel):
    pass

class GameStats(BaseModel):
    total_games: int
    wins: int
    losses: int
    win_rate: float
    average_guesses: float
    guess_distribution: dict
    streak: int
    max_streak: int

def get_cell_color(guess, chosen_word):
    """Simple color logic for Wordle"""
    output = {'cells': [], 'message': ''}
    check_occurrence = chosen_word

    # First pass: mark correct letters in green
    for i, letter in enumerate(guess):
        if letter == chosen_word[i]:
            output['cells'].append("#1fdb0dff")  # green
            check_occurrence = check_occurrence.replace(letter, "", 1)
        else:
            output['cells'].append(None)

    # Second pass: mark present but misplaced (yellow) OR wrong entirely (red)
    for i, letter in enumerate(guess):
        if output['cells'][i] is None:
            if letter in check_occurrence:
                output['cells'][i] = '#e4c53aff'  # yellow
                check_occurrence = check_occurrence.replace(letter, "", 1)
            else:
                output['cells'][i] = "#d71717ff"  # red

    is_win = all(color == "#1fdb0dff" for color in output['cells'])
    return output, is_win

def save_game_to_db(word: str, difficulty: str, guesses: int, won: bool, session_id: str):
    # Save completed game to database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get current time in SGT and format it properly
    sgt_time = get_sgt_time()
    # Format as YYYY-MM-DD HH:MM:SS without timezone info since we know it's SGT
    formatted_time = sgt_time.strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"Saving game with SGT timestamp: {formatted_time}")
    
    cursor.execute('''
        INSERT INTO games (word, difficulty, guesses, won, session_id, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (word, difficulty, guesses, won, session_id, formatted_time))
    
    # Update user stats
    cursor.execute('SELECT current_streak FROM user_stats WHERE id = 1')
    current_streak = cursor.fetchone()[0]
    
    if won:
        new_streak = current_streak + 1
    else:
        new_streak = 0
    
    # Get max streak
    cursor.execute('SELECT max_streak FROM user_stats WHERE id = 1')
    max_streak = cursor.fetchone()[0]
    new_max_streak = max(max_streak, new_streak)
    
    cursor.execute('''
        UPDATE user_stats 
        SET current_streak = ?, max_streak = ?, last_updated = ?
        WHERE id = 1
    ''', (new_streak, new_max_streak, formatted_time))
    
    conn.commit()
    conn.close()

def calculate_stats():
    """Calculate game statistics from database"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Get basic stats
    cursor.execute('SELECT COUNT(*) FROM games')
    total_games = cursor.fetchone()[0]
    
    if total_games == 0:
        conn.close()
        return {
            "total_games": 0,
            "wins": 0,
            "losses": 0,
            "win_rate": 0.0,
            "average_guesses": 0.0,
            "guess_distribution": {str(i): 0 for i in range(1, 7)},
            "streak": 0,
            "max_streak": 0,
            "difficulty_stats": {}
        }
    
    cursor.execute('SELECT COUNT(*) FROM games WHERE won = 1')
    wins = cursor.fetchone()[0]
    losses = total_games - wins
    win_rate = (wins / total_games) * 100 if total_games > 0 else 0
    
    # Calculate average guesses for won games only
    cursor.execute('SELECT AVG(guesses) FROM games WHERE won = 1')
    avg_result = cursor.fetchone()[0]
    average_guesses = round(avg_result, 1) if avg_result else 0
    
    # Guess distribution (only for won games)
    guess_distribution = {str(i): 0 for i in range(1, 7)}
    cursor.execute('SELECT guesses, COUNT(*) FROM games WHERE won = 1 GROUP BY guesses')
    for guesses, count in cursor.fetchall():
        if 1 <= guesses <= 6:
            guess_distribution[str(guesses)] = count
    
    # Get streak info
    cursor.execute('SELECT current_streak, max_streak FROM user_stats WHERE id = 1')
    streak_info = cursor.fetchone()
    current_streak, max_streak = streak_info if streak_info else (0, 0)
    
    # Get difficulty stats
    cursor.execute('''
        SELECT difficulty, 
               COUNT(*) as total,
               SUM(CASE WHEN won = 1 THEN 1 ELSE 0 END) as wins,
               AVG(CASE WHEN won = 1 THEN guesses END) as avg_guesses
        FROM games 
        GROUP BY difficulty
    ''')
    
    difficulty_stats = {}
    for row in cursor.fetchall():
        difficulty, total, wins_diff, avg_guesses_diff = row
        win_rate_diff = (wins_diff / total) * 100 if total > 0 else 0
        difficulty_stats[difficulty] = {
            "total_games": total,
            "wins": wins_diff,
            "win_rate": round(win_rate_diff, 1),
            "average_guesses": round(avg_guesses_diff, 1) if avg_guesses_diff else 0
        }
    
    conn.close()
    
    return {
        "total_games": total_games,
        "wins": wins,
        "losses": losses,
        "win_rate": round(win_rate, 1),
        "average_guesses": average_guesses,
        "guess_distribution": guess_distribution,
        "streak": current_streak,
        "max_streak": max_streak,
        "difficulty_stats": difficulty_stats
    }

@app.post("/new-game/{difficulty}")
async def new_game(difficulty: str, data: NewGameRequest):
    if difficulty not in difficulty_levels:
        raise HTTPException(status_code=404, detail="Difficulty not found")
    
    word_length = difficulty_levels[difficulty]
    word_bank = WORD_LISTS[word_length]
    
    chosen_word = random.choice(word_bank)
    session_id = f"{difficulty}_{random.randint(1000, 9999)}"
    
    game_sessions[session_id] = {
        "word": chosen_word,
        "difficulty": difficulty,
        "guesses": 0,
        "max_guesses": 6,
        "is_complete": False
    }
    
    return {"session_id": session_id, "word_length": word_length, "max_guesses": 6}

@app.post("/guess/{session_id}")
async def make_guess(session_id: str, data: GuessRequest):
    if session_id not in game_sessions:
        raise HTTPException(status_code=404, detail="Game session not found")
    
    session = game_sessions[session_id]
    if session["is_complete"]:
        raise HTTPException(status_code=400, detail="Game is already complete")
    
    guess = data.guess.upper()
    chosen_word = session["word"]
    word_length = len(chosen_word)
    
    if len(guess) != word_length:
        raise HTTPException(status_code=400, detail=f"Guess must be {word_length} letters")
    
    # Validate that the guess is a real word
    if not is_valid_word(guess, word_length):
        raise HTTPException(status_code=400, detail=f"'{guess}' is not a valid word")
    
    result, is_win = get_cell_color(guess, chosen_word)
    session["guesses"] += 1
    
    if is_win:
        session["is_complete"] = True
        result["message"] = "You win!"
        # Save completed game to database
        save_game_to_db(chosen_word, session["difficulty"], session["guesses"], True, session_id)
    elif session["guesses"] >= session["max_guesses"]:
        session["is_complete"] = True
        result["message"] = f"Game Over! The word was {chosen_word}"
        # Save completed game to database
        save_game_to_db(chosen_word, session["difficulty"], session["guesses"], False, session_id)
    
    return {"cells": result['cells'], "message": result['message'], "won": is_win, "game_over": session["is_complete"]}


# Add this route to your main.py
@app.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: dict = Body(...),
    current_user: dict = Depends(auth_manager.get_current_user)
):
    """Update user profile"""
    try:
        # Update user in database
        updated_user = auth_manager.update_user_profile(
            current_user["id"], 
            profile_data
        )
        return UserResponse(**updated_user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update profile: {str(e)}"
        )

@app.get("/history")
async def get_history():
    """Get recent game history"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT word, difficulty, guesses, won, timestamp 
        FROM games 
        ORDER BY timestamp DESC 
        LIMIT 20
    ''')
    
    games = []
    for row in cursor.fetchall():
        word, difficulty, guesses, won, timestamp = row
        games.append({
            "word": word,
            "difficulty": difficulty,  
            "guesses": guesses,
            "won": bool(won),
            "timestamp": timestamp
        })
    
    conn.close()
    return {"games": games}

@app.get("/stats")
async def get_stats():
    """Get user statistics"""
    return calculate_stats()

@app.get("/leaderboard")
async def get_leaderboard():
    """Get leaderboard with top players"""
    # Mock leaderboard data for now
    mock_leaderboard = [
        {"rank": 1, "name": "WordMaster2024", "wins": 156, "winRate": 89, "gamesPlayed": 175},
        {"rank": 2, "name": "GuessGenius", "wins": 142, "winRate": 85, "gamesPlayed": 167},
        {"rank": 3, "name": "LetterLegend", "wins": 138, "winRate": 82, "gamesPlayed": 168},
        {"rank": 4, "name": "WordWizard", "wins": 128, "winRate": 76, "gamesPlayed": 168},
        {"rank": 5, "name": "PuzzlePro", "wins": 124, "winRate": 78, "gamesPlayed": 159},
        {"rank": 6, "name": "VocabViper", "wins": 119, "winRate": 74, "gamesPlayed": 161},
        {"rank": 7, "name": "LetterLord", "wins": 115, "winRate": 73, "gamesPlayed": 158},
        {"rank": 8, "name": "WordWarrior", "wins": 112, "winRate": 72, "gamesPlayed": 156},
        {"rank": 9, "name": "GuessGuru", "wins": 108, "winRate": 71, "gamesPlayed": 152},
        {"rank": 10, "name": "PuzzlePilot", "wins": 105, "winRate": 70, "gamesPlayed": 150}
    ]
    return {"leaderboard": mock_leaderboard}

@app.post("/reset-stats")
async def reset_stats():
    """Reset all game statistics"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM games')
    cursor.execute('UPDATE user_stats SET current_streak = 0, max_streak = 0 WHERE id = 1')
    
    conn.commit()
    conn.close()
    
    return {"message": "Statistics reset successfully"}

@app.post("/validate-word")
async def validate_word(data: GuessRequest):
    """Check if a word is valid for any difficulty level"""
    word = data.guess.upper()
    word_length = len(word)
    
    if word_length not in [4, 5, 6]:
        return {"valid": False, "message": "Word must be 4, 5, or 6 letters long"}
    
    is_valid = is_valid_word(word, word_length)
    return {
        "valid": is_valid, 
        "message": "Valid word" if is_valid else f"'{word}' is not a valid word"
    }

# Authentication endpoints
@app.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user"""
    try:
        # Create user
        user = auth_manager.create_user(
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = auth_manager.create_access_token(
            data={"sub": user["username"]}, 
            expires_delta=access_token_expires
        )
        
        # Return token and user info
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse(**user)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )

@app.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    """Login user and return access token"""
    user = auth_manager.authenticate_user(user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = auth_manager.create_access_token(
        data={"sub": user["username"]}, 
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user)
    }

@app.get("/me", response_model=UserResponse)
async def get_current_user(current_user: dict = Depends(auth_manager.get_current_user)):
    """Get current user information"""
    return UserResponse(**current_user)

# Google OAuth endpoints
@app.get("/auth/google", response_model=GoogleAuthResponse)
async def google_auth():
    """Get Google OAuth authorization URL"""
    auth_url = google_oauth.get_authorization_url()
    return {"auth_url": auth_url}

@app.post("/auth/google/callback", response_model=Token)
async def google_auth_callback(auth_request: GoogleAuthRequest):
    """Handle Google OAuth callback"""
    try:
        # Process Google OAuth
        google_user_info = google_oauth.process_google_auth(auth_request.code)
        
        # Create or update user
        user = auth_manager.create_or_update_google_user(google_user_info)
        
        # Create access token
        access_token_expires = timedelta(minutes=30)
        access_token = auth_manager.create_access_token(
            data={"sub": user["username"]}, 
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": UserResponse(**user)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )

@app.get("/")
async def root():
    return {"message": "Wordle Backend is running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
