#!/usr/bin/env python3

import threading
import time
import requests
import json
from app import app, db, Customer

def run_flask_app():
    """Run Flask app in a separate thread"""
    app.run(debug=False, use_reloader=False, port=5001)

def test_customer_crud():
    """Test all Customer CRUD operations"""
    BASE_URL = "http://127.0.0.1:5001"
    
    print("Testing Customer CRUD Endpoints")
    print("===============================")
    
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
        response = requests.post(f"{BASE_URL}/customers", json=customer_data)
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
        response = requests.get(f"{BASE_URL}/customers")
        print(f"Status Code: {response.status_code}")
        customers = response.json()
        print(f"Number of customers: {len(customers)}")
        print(f"✅ READ all successful")
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
            print(f"✅ READ by ID successful")
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
            print(f"✅ UPDATE successful")
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
            print(f"✅ DELETE successful")
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
            print(f"✅ Customer properly deleted (404 expected)")
        else:
            print("❌ Customer still exists after deletion")
    except Exception as e:
        print(f"❌ Error checking deleted customer: {e}")
    
    print("\n=== All tests completed ===")

if __name__ == "__main__":
    # Create database tables
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    
    # Run the tests
    test_customer_crud()