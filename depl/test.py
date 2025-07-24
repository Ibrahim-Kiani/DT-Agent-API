import requests
import json

# Test script for the deployed API
def test_api(base_url):
    """Test the deployed Smart Hospital AI API"""
    
    print(f"Testing API at: {base_url}")
    print("=" * 50)
    
    # Test 1: Health check
    print("1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("-" * 30)
    
    # Test 2: Chat endpoint
    print("2. Testing chat endpoint...")
    test_messages = [
        "Show me all patients currently in the hospital",
        "What are the current alerts?",
        "Hello, how can you help me with hospital management?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n2.{i} Testing message: '{message}'")
        try:
            payload = {
                "message": message,
                "conversation_history": []
            }
            response = requests.post(
                f"{base_url}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {data['response'][:200]}...")
                print(f"Tools used: {data.get('tools_used', [])}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
    
    print("-" * 30)
    
    # Test 3: Hospital data endpoints
    print("3. Testing hospital data endpoints...")
    endpoints = ['patients', 'alerts', 'staff', 'rooms']
    
    for endpoint in endpoints:
        print(f"\n3.{endpoints.index(endpoint)+1} Testing /{endpoint}...")
        try:
            response = requests.get(f"{base_url}/hospital-data/{endpoint}")
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"Data type: {type(data)}")
                if isinstance(data, list):
                    print(f"Number of items: {len(data)}")
                elif isinstance(data, dict):
                    print(f"Keys: {list(data.keys())}")
            else:
                print(f"Error: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    # Replace with your deployed API URL
    api_url = "https://your-app-name.onrender.com"
    
    # For local testing
    # api_url = "http://localhost:5000"
    
    test_api(api_url)