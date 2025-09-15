import requests
import json

BASE_URL = "http://localhost:8000"

# Test the requests endpoint directly
def test_requests_endpoint():
    # First, login as dean to get token
    login_data = {'username': 'test_dean', 'password': 'testpass123'}
    response = requests.post(f'{BASE_URL}/api/auth/login/', json=login_data)
    
    print(f"Login status: {response.status_code}")
    print(f"Login response text: {response.text}")
    
    if response.status_code == 200:
        token = response.json()['access']
        print(f"Token received: {token[:20]}...")
        
        # Now test the requests endpoint
        request_data = {
            "title": "Simple Test Request",
            "description": "Test request",
            "priority": "HIGH",
            "items": [{"product": 1, "quantity": 5}]
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        response = requests.post(f'{BASE_URL}/api/request/', json=request_data, headers=headers)
        
        print(f"\nRequest creation status: {response.status_code}")
        print(f"Request creation response text: {response.text}")
        
        # Check if it's a redirect (common with trailing slash issues)
        if response.history:
            print(f"Redirected: {[r.status_code for r in response.history]}")
            
    else:
        print("Login failed")

if __name__ == "__main__":
    test_requests_endpoint()