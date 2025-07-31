#!/usr/bin/env python3
import requests
import json

def test_backend():
    try:
        # Test new game endpoint
        response = requests.post('http://localhost:8000/new-game/medium', 
                               json={}, 
                               headers={'Content-Type': 'application/json'})
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("Backend is working correctly!")
            print(f"Session ID: {data.get('session_id')}")
            print(f"Word Length: {data.get('word_length')}")
        else:
            print("Backend returned an error")
            
    except requests.exceptions.ConnectionError:
        print("Could not connect to backend server. Make sure it's running on port 8000.")
    except Exception as e:
        print(f"Error testing backend: {e}")

if __name__ == "__main__":
    test_backend()
