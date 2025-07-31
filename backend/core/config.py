"""
Core configuration for the Wordle backend application
"""
import os
from typing import List

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours for development

# Database configuration
DATABASE_PATH = "wordle_stats.db"

# Game configuration
MAX_GUESSES = 6
DIFFICULTY_WORD_LENGTHS = {
    "easy": 4,
    "medium": 5,
    "hard": 6
}

# CORS configuration
ALLOWED_ORIGINS: List[str] = [
    "http://localhost:5173", 
    "http://localhost:5174", 
    "http://localhost:3000",
    "https://frontend-production-3bb7.up.railway.app"
]

# Google OAuth configuration
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")

# Timezone configuration
DEFAULT_TIMEZONE = "America/New_York"
