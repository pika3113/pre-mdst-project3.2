#!/usr/bin/env python3
"""
Debug script to test balance service in Docker container
"""
import sys
import traceback
from core.database import db_manager
from services.balance_service import balance_service

def main():
    try:
        print("=== Testing Database Connection ===")
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"Available tables: {tables}")
        
        conn.close()
        
        print("\n=== Testing Balance Service Initialization ===")
        # This should initialize tables
        balance_service.init_balance_tables()
        print("Balance tables initialized successfully")
        
        print("\n=== Testing get_user_balance with fake user ===")
        # Test with a fake user ID to see if the error occurs
        try:
            result = balance_service.get_user_balance(1)
            print(f"Balance service test successful: {result}")
        except Exception as e:
            print(f"Error in get_user_balance: {e}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
