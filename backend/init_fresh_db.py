#!/usr/bin/env python3
"""
Initialize a fresh database with all required tables
"""
import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import db_manager
from services.auth_service import AuthManager

def main():
    print("Initializing fresh database...")
    
    # Remove existing database if it exists
    if os.path.exists(db_manager.db_path):
        os.remove(db_manager.db_path)
        print(f"Removed existing database: {db_manager.db_path}")
    
    # Initialize main database tables
    db_manager.init_database()
    print("Main database tables created")
    
    # Initialize auth tables
    auth_manager = AuthManager(db_manager.db_path)
    auth_manager.init_auth_tables()
    print("Auth tables created")
    
    print("Database initialization complete!")
    print(f"Database location: {db_manager.db_path}")

if __name__ == "__main__":
    main()
