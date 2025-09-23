"""
Test script for JWT token authentication functionality.
"""

import requests

BASE_URL = "http://127.0.0.1:5000"


def test_token_authentication():
    """Test the complete token authentication flow."""
    
    print("🔐 Testing JWT Token Authentication System")
    print("=" * 50)
    
    # Test 1: Create a customer with password
    print("\n1. Creating a customer with password...")
    customer_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "555-0123",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/customers/", json=customer_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 201:
        customer = response.json()
        print(f"✅ Customer created: {customer['first_name']} {customer['last_name']}")
        customer_id = customer['id']
    else:
        print(f"❌ Failed to create customer: {response.text}")
        return
    
    # Test 2: Login with correct credentials
    print("\n2. Testing login with correct credentials...")
    login_data = {
        "email": "john.doe@example.com",
        "password": "securepassword123"
    }
    
    response = requests.post(f"{BASE_URL}/customers/login", json=login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        login_result = response.json()
        print("✅ Login successful!")
        print(f"Token: {login_result['token'][:50]}...")
        token = login_result['token']
    else:
        print(f"❌ Login failed: {response.text}")
        return
    
    # Test 3: Login with wrong credentials
    print("\n3. Testing login with wrong credentials...")
    wrong_login_data = {
        "email": "john.doe@example.com",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/customers/login", json=wrong_login_data)
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Login correctly rejected with wrong password")
    else:
        print(f"❌ Unexpected response: {response.text}")
    
    # Test 4: Access protected route without token
    print("\n4. Testing protected route without token...")
    response = requests.get(f"{BASE_URL}/customers/my-tickets")
    print(f"Status: {response.status_code}")
    if response.status_code == 401:
        print("✅ Protected route correctly rejected without token")
    else:
        print(f"❌ Unexpected response: {response.text}")
    
    # Test 5: Access protected route with valid token
    print("\n5. Testing protected route with valid token...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/customers/my-tickets", headers=headers)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        tickets_result = response.json()
        print("✅ Protected route accessed successfully!")
        print(f"Found {len(tickets_result['tickets'])} service tickets")
    else:
        print(f"❌ Failed to access protected route: {response.text}")
    
    # Test 6: Try to update another customer's information
    print("\n6. Testing authorization (trying to update another customer)...")
    # First create another customer
    other_customer_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "email": "jane.smith@example.com",
        "phone_number": "555-0456",
        "password": "anotherpassword"
    }
    
    response = requests.post(f"{BASE_URL}/customers/", json=other_customer_data)
    if response.status_code == 201:
        other_customer = response.json()
        other_customer_id = other_customer['id']
        
        # Try to update other customer with John's token
        update_data = {"first_name": "Updated"}
        response = requests.put(
            f"{BASE_URL}/customers/{other_customer_id}",
            json=update_data,
            headers=headers
        )
        print(f"Status: {response.status_code}")
        if response.status_code == 403:
            print("✅ Authorization correctly prevents updating other customers")
        else:
            print(f"❌ Unexpected response: {response.text}")
    
    # Test 7: Update own information
    print("\n7. Testing updating own customer information...")
    update_data = {"first_name": "Johnny"}
    response = requests.put(
        f"{BASE_URL}/customers/{customer_id}",
        json=update_data,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        updated_customer = response.json()
        print(f"✅ Successfully updated customer: {updated_customer['first_name']}")
    else:
        print(f"❌ Failed to update customer: {response.text}")
    
    print("\n" + "=" * 50)
    print("🎉 Token authentication testing complete!")


if __name__ == "__main__":
    try:
        test_token_authentication()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the Flask app is running on http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error during testing: {e}")