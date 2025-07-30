#!/usr/bin/env python3
"""
Quick test script to verify authentication system is working
"""
import requests
import json
import sys

BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint, description):
    """Test an API endpoint"""
    try:
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
        if response.status_code == 200:
            print(f"✅ {description}: OK")
            return True
        else:
            print(f"❌ {description}: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ {description}: Connection failed - {e}")
        return False

def test_auth_endpoints():
    """Test authentication-specific endpoints"""
    print("🔐 Testing Authentication Endpoints:")
    print("-" * 50)
    
    # Test basic connectivity
    test_endpoint("/", "Backend connectivity")
    
    # Test Google OAuth endpoint
    test_endpoint("/auth/google", "Google OAuth URL endpoint")
    
    # Test registration endpoint (POST - expect method not allowed for GET)
    try:
        response = requests.get(f"{BASE_URL}/register", timeout=5)
        if response.status_code == 405:  # Method not allowed is expected
            print("✅ Registration endpoint: Available (POST method)")
        else:
            print(f"⚠️  Registration endpoint: Unexpected response {response.status_code}")
    except:
        print("❌ Registration endpoint: Connection failed")
    
    # Test login endpoint (POST - expect method not allowed for GET)
    try:
        response = requests.get(f"{BASE_URL}/login", timeout=5)
        if response.status_code == 405:  # Method not allowed is expected
            print("✅ Login endpoint: Available (POST method)")
        else:
            print(f"⚠️  Login endpoint: Unexpected response {response.status_code}")
    except:
        print("❌ Login endpoint: Connection failed")

def test_game_endpoints():
    """Test game endpoints still work"""
    print("\n🎮 Testing Game Endpoints:")
    print("-" * 50)
    
    # Test new game endpoint (POST)
    try:
        response = requests.post(f"{BASE_URL}/new-game/medium", 
                               json={}, 
                               timeout=5)
        if response.status_code == 200:
            print("✅ New game endpoint: OK")
        else:
            print(f"❌ New game endpoint: HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ New game endpoint: Failed - {e}")
    
    # Test stats endpoint
    test_endpoint("/stats", "Game statistics endpoint")

def main():
    print("🚀 Wordle Authentication System Test")
    print("=" * 50)
    print("Testing if the authentication system is running correctly...\n")
    
    test_auth_endpoints()
    test_game_endpoints()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nIf all tests pass, your authentication system is ready!")
    print("If tests fail, check:")
    print("- Docker containers are running: docker-compose ps")
    print("- Backend logs: docker-compose logs backend")
    print("- .env file is configured properly")

if __name__ == "__main__":
    main()
