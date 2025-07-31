import requests
import json

def test_endpoints():
    base_url = "http://localhost:8000"
    
    # Test root endpoint
    try:
        response = requests.get(f"{base_url}/")
        print(f"Root endpoint: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"Root endpoint error: {e}")
    
    # Test stats endpoint
    try:
        response = requests.get(f"{base_url}/stats")
        print(f"Stats endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"Stats data: {response.json()}")
        else:
            print(f"Stats error: {response.text}")
    except Exception as e:
        print(f"Stats endpoint error: {e}")
    
    # Test history endpoint
    try:
        response = requests.get(f"{base_url}/history")
        print(f"History endpoint: {response.status_code}")
        if response.status_code == 200:
            print(f"History data: {response.json()}")
        else:
            print(f"History error: {response.text}")
    except Exception as e:
        print(f"History endpoint error: {e}")

if __name__ == "__main__":
    test_endpoints()
