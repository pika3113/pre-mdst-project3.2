#!/usr/bin/env python3
"""
Debug script to test auth service in Docker container
"""
import sys
import traceback
from services.auth_service import AuthManager
from core.database import db_manager

def main():
    try:
        print("=== Testing Auth Manager ===")
        auth_manager = AuthManager(db_manager.db_path)
        
        # Check what users exist
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, email FROM users")
        users = cursor.fetchall()
        print(f"Users in database: {users}")
        
        # Test getting a user by username
        if users:
            first_user = users[0]
            user_dict = auth_manager.get_user_by_username(first_user[1])
            print(f"User dict structure: {user_dict}")
            print(f"User ID accessible: {user_dict.get('id') if user_dict else 'No user'}")
        else:
            print("No users found in database")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
