#!/usr/bin/env python3
"""
Comprehensive test suite for Customer CRUD operations using Application Factory Pattern.
"""

import threading
import time
import requests
from app import create_app
from app.extensions import db


def run_flask_app(app):
    """Run Flask app in a separate thread."""
    app.run(debug=False, use_reloader=False, port=5001)


def test_customer_crud():
    """Test all Customer CRUD operations."""
    BASE_URL = "http://127.0.0.1:5001"
    
    print("Testing Customer CRUD Endpoints (Application Factory Pattern)")
    print("============================================================")
    
    # Wait for Flask to start
    print("Waiting for Flask server to start...")
    time.sleep(3)
    
    # Test CREATE
    print("\n=== Testing CREATE Customer ===")
    import time as time_module
    unique_email = f"john.doe.{int(time_module.time())}@email.com"
    customer_data = {
        "first_name": "John",
        "last_name": "Doe",
        "email": unique_email, 
        "phone_number": "555-0123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/customers/", json=customer_data)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 201:
            customer = response.json()
            customer_id = customer.get('id')
            print(f"✅ CREATE successful - Customer ID: {customer_id}")
        else:
            print("❌ CREATE failed")
            return
    except Exception as e:
        print(f"❌ CREATE error: {e}")
        return
    
    # Test READ all customers
    print("\n=== Testing GET All Customers ===")
    try:
        response = requests.get(f"{BASE_URL}/customers/")
        print(f"Status Code: {response.status_code}")
        customers = response.json()
        print(f"Number of customers: {len(customers)}")
        print("✅ READ all successful")
    except Exception as e:
        print(f"❌ READ all error: {e}")
    
    # Test READ single customer
    print(f"\n=== Testing GET Customer by ID ({customer_id}) ===")
    try:
        response = requests.get(f"{BASE_URL}/customers/{customer_id}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            customer = response.json()
            print(f"Customer: {customer['first_name']} {customer['last_name']}")
            print("✅ READ by ID successful")
        else:
            print("❌ READ by ID failed")
    except Exception as e:
        print(f"❌ READ by ID error: {e}")
    
    # Test UPDATE customer
    print(f"\n=== Testing UPDATE Customer ({customer_id}) ===")
    update_data = {
        "first_name": "Jane",
        "last_name": "Smith",
        "phone_number": "555-9876"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/customers/{customer_id}", json=update_data)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            updated_customer = response.json()
            print(f"Updated Customer: {updated_customer['first_name']} {updated_customer['last_name']}")
            print("✅ UPDATE successful")
        else:
            print("❌ UPDATE failed")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ UPDATE error: {e}")
    
    # Test DELETE customer
    print(f"\n=== Testing DELETE Customer ({customer_id}) ===")
    try:
        response = requests.delete(f"{BASE_URL}/customers/{customer_id}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ DELETE successful")
        else:
            print("❌ DELETE failed")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ DELETE error: {e}")
    
    # Test READ after deletion (should return 404)
    print(f"\n=== Testing GET Customer after deletion ({customer_id}) ===")
    try:
        response = requests.get(f"{BASE_URL}/customers/{customer_id}")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 404:
            print("✅ Customer properly deleted (404 expected)")
        else:
            print("❌ Customer still exists after deletion")
    except Exception as e:
        print(f"❌ Error checking deleted customer: {e}")
    
    # Test API info endpoints
    print(f"\n=== Testing API Info Endpoints ===")
    try:
        # Test root endpoint
        response = requests.get(f"{BASE_URL}/")
        print(f"Root endpoint status: {response.status_code}")
        if response.status_code == 200:
            info = response.json()
            print(f"API message: {info.get('message')}")
            print(f"✅ Root endpoint successful")
        
        # Test health endpoint
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health endpoint status: {response.status_code}")
        if response.status_code == 200:
            health = response.json()
            print(f"Health status: {health.get('status')}")
            print(f"✅ Health endpoint successful")
    except Exception as e:
        print(f"❌ API info endpoints error: {e}")
    
    print("\n=== All tests completed ===")


def main():
    """Main test function."""
    # Create app with testing configuration
    app = create_app('testing')
    
    # Create database tables within app context
    with app.app_context():
        db.create_all()
        print("Test database tables created successfully!")
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask_app, args=(app,), daemon=True)
    flask_thread.start()
    
    # Run the tests
    test_customer_crud()


if __name__ == "__main__":
    main()