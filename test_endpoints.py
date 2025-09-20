#!/usr/bin/env python3

import requests
import json
import time

BASE_URL = "http://127.0.0.1:5000"

def test_create_customer():
    """Test creating a new customer"""
    print("=== Testing CREATE Customer ===")
    
    # Use a unique email for each test run to avoid conflicts
    customer_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": f"john.doe.{int(time.time())}@email.com",
        "phone_number": "555-0123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/customers", json=customer_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json() if response.status_code == 201 else None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_get_all_customers():
    """Test getting all customers"""
    print("\n=== Testing GET All Customers ===")
    
    try:
        response = requests.get(f"{BASE_URL}/customers")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_get_customer_by_id(customer_id):
    """Test getting a customer by ID"""
    print(f"\n=== Testing GET Customer by ID ({customer_id}) ===")
    
    try:
        response = requests.get(f"{BASE_URL}/customers/{customer_id}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_update_customer(customer_id):
    """Test updating a customer"""
    print(f"\n=== Testing UPDATE Customer ({customer_id}) ===")
    
    update_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "phone_number": "555-9876"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/customers/{customer_id}", json=update_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_delete_customer(customer_id):
    """Test deleting a customer"""
    print(f"\n=== Testing DELETE Customer ({customer_id}) ===")
    
    try:
        response = requests.delete(f"{BASE_URL}/customers/{customer_id}")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("Testing Customer CRUD Endpoints")
    print("===============================")
    
    # Wait a moment for Flask to be ready
    print("Waiting for Flask server to be ready...")
    time.sleep(2)
    
    # Test CREATE
    customer = test_create_customer()
    if not customer:
        print("CREATE test failed - stopping tests")
        return
    
    customer_id = customer.get('id')
    
    # Test READ all
    test_get_all_customers()
    
    # Test READ by ID
    test_get_customer_by_id(customer_id)
    
    # Test UPDATE
    test_update_customer(customer_id)
    
    # Test READ by ID again to see changes
    test_get_customer_by_id(customer_id)
    
    # Test DELETE
    test_delete_customer(customer_id)
    
    # Test READ by ID after deletion (should return 404)
    test_get_customer_by_id(customer_id)
    
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    main()