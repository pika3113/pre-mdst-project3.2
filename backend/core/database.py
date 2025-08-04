"""
Database initialization and connection utilities
"""
import sqlite3
from typing import Optional
from .config import DATABASE_PATH


class DatabaseManager:
    """Manages database connections and initialization"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable row access by column name
        return conn
    
    def init_database(self):
        """Initialize all database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Games table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    word TEXT NOT NULL,
                    difficulty TEXT NOT NULL,
                    guesses TEXT,
                    guess_count INTEGER,
                    won BOOLEAN,
                    completed_at DATETIME DEFAULT NULL,
                    time_taken INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS statistics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER UNIQUE,
                    total_games INTEGER DEFAULT 0,
                    games_won INTEGER DEFAULT 0,
                    current_streak INTEGER DEFAULT 0,
                    max_streak INTEGER DEFAULT 0,
                    guess_distribution TEXT DEFAULT "{}",
                    last_game_date DATE,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            # Add difficulty statistics table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS difficulty_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    difficulty TEXT,
                    total_games INTEGER DEFAULT 0,
                    games_won INTEGER DEFAULT 0,
                    current_streak INTEGER DEFAULT 0,
                    max_streak INTEGER DEFAULT 0,
                    guess_distribution TEXT DEFAULT "{}",
                    average_guesses REAL DEFAULT 0.0,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    UNIQUE(user_id, difficulty)
                )
            ''')
            
            conn.commit()
        finally:
            conn.close()

# Global database manager instance
db_manager = DatabaseManager()
