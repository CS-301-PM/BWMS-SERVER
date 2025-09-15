# test_stores_access.py
import requests
import json

BASE_URL = "http://localhost:8000"

def test_stores_access():
    print("Testing Stores Manager access to requests...")
    
    # Login as stores manager
    login_data = {'username': 'stores_manager1', 'password': 'testpass123'}
    response = requests.post(f'{BASE_URL}/api/auth/login/', json=login_data)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.text}")
        return False
        
    token = response.json()['access']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    # Test 1: Get all requests
    print("\n1. Testing GET /api/requests/requests/")
    response = requests.get(f'{BASE_URL}/api/requests/requests/', headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        requests_data = response.json()
        print(f"✅ Success! Found {len(requests_data)} requests")
        for req in requests_data:
            print(f"   - Request #{req['id']}: {req.get('product_detail', {}).get('name', 'Unknown')} by {req.get('requested_by_name', 'Unknown')}")
    else:
        print(f"❌ Failed: {response.text}")
        return False
    
    # Test 2: Get pending requests
    print("\n2. Testing GET /api/requests/requests/pending/")
    response = requests.get(f'{BASE_URL}/api/requests/requests/pending/', headers=headers)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        pending_requests = response.json()
        print(f"✅ Success! Found {len(pending_requests)} pending requests")
    else:
        print(f"❌ Failed: {response.text}")
    
    # Test 3: Try to update a request status
    print("\n3. Testing PATCH /api/requests/requests/<id>/update_status/")
    if requests_data:
        first_request_id = requests_data[0]['id']
        update_data = {
            'status': 'APPROVED',
            'stores_comment': 'Test approval by stores manager'
        }
        response = requests.patch(
            f'{BASE_URL}/api/requests/requests/{first_request_id}/update_status/',
            headers=headers,
            json=update_data
        )
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Success! Request status updated")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed: {response.text}")
    
    return True

if __name__ == "__main__":
    success = test_stores_access()
    print(f"\n{'✅ Test passed!' if success else '❌ Test failed!'}")