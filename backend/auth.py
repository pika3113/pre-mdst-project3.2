from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import sqlite3
import os

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token scheme
security = HTTPBearer()

class AuthManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_auth_tables()
    
    def init_auth_tables(self):
        """Initialize authentication-related database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                hashed_password TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                google_id TEXT UNIQUE,
                profile_picture TEXT,
                auth_provider TEXT DEFAULT 'email'
            )
        ''')
        
        # Add new columns to existing users table if they don't exist
        cursor.execute('PRAGMA table_info(users)')
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'google_id' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN google_id TEXT UNIQUE')
        if 'profile_picture' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN profile_picture TEXT')
        if 'auth_provider' not in columns:
            cursor.execute('ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT "email"')
        
        # Create user_sessions table for additional session management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL,
                expires_at DATETIME NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Update games table to link with users (add user_id column if not exists)
        cursor.execute('PRAGMA table_info(games)')
        columns = [column[1] for column in cursor.fetchall()]
        if 'user_id' not in columns:
            cursor.execute('ALTER TABLE games ADD COLUMN user_id INTEGER REFERENCES users(id)')
        
        # Update user_stats table to link with users
        cursor.execute('PRAGMA table_info(user_stats)')
        columns = [column[1] for column in cursor.fetchall()]
        if 'user_id' not in columns:
            cursor.execute('ALTER TABLE user_stats ADD COLUMN user_id INTEGER REFERENCES users(id)')
        
        conn.commit()
        conn.close()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return payload
        except JWTError:
            return None
    
    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Get user by username"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM users WHERE username = ? AND is_active = 1", 
            (username,)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM users WHERE email = ? AND is_active = 1", 
            (email,)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None
    
    def create_user(self, username: str, email: str, password: str) -> dict:
        """Create a new user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if username or email already exists
        cursor.execute(
            "SELECT COUNT(*) FROM users WHERE username = ? OR email = ?", 
            (username, email)
        )
        if cursor.fetchone()[0] > 0:
            conn.close()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Hash password and create user
        hashed_password = self.get_password_hash(password)
        cursor.execute(
            "INSERT INTO users (username, email, hashed_password) VALUES (?, ?, ?)",
            (username, email, hashed_password)
        )
        user_id = cursor.lastrowid
        
        # Create initial user stats
        cursor.execute(
            "INSERT INTO user_stats (user_id) VALUES (?)",
            (user_id,)
        )
        
        conn.commit()
        conn.close()
        
        return {
            "id": user_id,
            "username": username,
            "email": email,
            "is_active": True
        }
    
    def get_user_by_google_id(self, google_id: str) -> Optional[dict]:
        """Get user by Google ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM users WHERE google_id = ? AND is_active = 1", 
            (google_id,)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return dict(user)
        return None
    
    def create_or_update_google_user(self, google_user_info: dict) -> dict:
        """Create new user from Google OAuth or update existing user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        google_id = google_user_info.get("google_id")
        email = google_user_info.get("email")
        name = google_user_info.get("name", "")
        picture = google_user_info.get("picture", "")
        
        # Check if user already exists by Google ID
        existing_user = self.get_user_by_google_id(google_id)
        if existing_user:
            # Update existing user's last login and picture
            cursor.execute(
                """UPDATE users SET 
                   last_login = CURRENT_TIMESTAMP, 
                   profile_picture = ? 
                   WHERE google_id = ?""",
                (picture, google_id)
            )
            conn.commit()
            conn.close()
            return existing_user
        
        # Check if user exists by email (linking existing account)
        existing_user = self.get_user_by_email(email)
        if existing_user:
            # Link Google account to existing user
            cursor.execute(
                """UPDATE users SET 
                   google_id = ?, 
                   profile_picture = ?, 
                   auth_provider = 'google',
                   last_login = CURRENT_TIMESTAMP 
                   WHERE email = ?""",
                (google_id, picture, email)
            )
            conn.commit()
            conn.close()
            return self.get_user_by_email(email)
        
        # Generate unique username from name/email
        base_username = self._generate_username_from_name(name, email)
        username = self._ensure_unique_username(base_username)
        
        # Create new user
        cursor.execute(
            """INSERT INTO users 
               (username, email, google_id, profile_picture, auth_provider, hashed_password) 
               VALUES (?, ?, ?, ?, 'google', NULL)""",
            (username, email, google_id, picture)
        )
        user_id = cursor.lastrowid
        
        # Create initial user stats
        cursor.execute(
            "INSERT INTO user_stats (user_id) VALUES (?)",
            (user_id,)
        )
        
        conn.commit()
        conn.close()
        
        return {
            "id": user_id,
            "username": username,
            "email": email,
            "google_id": google_id,
            "profile_picture": picture,
            "auth_provider": "google",
            "is_active": True
        }
    
    def _generate_username_from_name(self, name: str, email: str) -> str:
        """Generate a username from name or email"""
        if name:
            # Use name, remove spaces and special characters
            username = name.lower().replace(" ", "").replace("-", "").replace("_", "")
            username = ''.join(c for c in username if c.isalnum())
        else:
            # Use email prefix
            username = email.split("@")[0].lower()
        
        # Ensure minimum length
        if len(username) < 3:
            username = f"user{username}"
        
        # Ensure maximum length
        if len(username) > 15:
            username = username[:15]
            
        return username
    
    def _ensure_unique_username(self, base_username: str) -> str:
        """Ensure username is unique by adding numbers if needed"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        username = base_username
        counter = 1
        
        while True:
            cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            if cursor.fetchone()[0] == 0:
                break
            username = f"{base_username}{counter}"
            counter += 1
        
        conn.close()
        return username
    
    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate a user with username/password"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not self.verify_password(password, user["hashed_password"]):
            return None
        
        # Update last login
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user["id"],)
        )
        conn.commit()
        conn.close()
        
        return user
    
    def get_current_user(self, credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
        """Get current user from JWT token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        payload = self.verify_token(credentials.credentials)
        if payload is None:
            raise credentials_exception
        
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        user = self.get_user_by_username(username)
        if user is None:
            raise credentials_exception
        
        return user
