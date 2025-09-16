# debug_approvals.py
import requests
import json

BASE_URL = "http://localhost:8000"

def debug_approvals():
    # Login as stores manager
    login_data = {'username': 'stores_manager1', 'password': 'testpass123'}
    response = requests.post(f'{BASE_URL}/api/auth/login/', json=login_data)
    token = response.json()['access']
    
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Check pending approvals
    print("Checking pending approvals...")
    response = requests.get(f'{BASE_URL}/api/approvals/approvals/my_pending_approvals/', headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Check all approvals
    print("\nChecking all approvals...")
    response = requests.get(f'{BASE_URL}/api/approvals/approvals/', headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Check the specific request
    print("\nChecking request #10...")
    response = requests.get(f'{BASE_URL}/api/requests/requests/10/', headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")

if __name__ == "__main__":
    debug_approvals()