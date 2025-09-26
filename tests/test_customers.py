"""
Pytest-based tests for Customer CRUD operations.

These tests use the Flask test client and pytest fixtures to ensure
fast and isolated testing of the customer endpoints.
"""

import time


def test_root_and_health_endpoints(client):
    """Test the root and health check endpoints."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json["message"] == "Welcome to the Mechanic Shop API!"

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "ok"


def test_customer_crud_flow(client):
    """Test the full CRUD lifecycle for a customer."""
    # --- 1. CREATE Customer ---
    unique_email = f"test.user.{int(time.time())}@example.com"
    customer_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": unique_email,
        "phone_number": "555-1234",
        "password": "a-secure-password",
    }
    response = client.post("/customers/", json=customer_data)
    assert response.status_code == 201
    created_customer = response.json
    customer_id = created_customer["id"]
    assert created_customer["first_name"] == "Test"

    # --- 2. LOGIN to get a token ---
    login_data = {"email": unique_email, "password": "a-secure-password"}
    response = client.post("/customers/login", json=login_data)
    assert response.status_code == 200
    token = response.json["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # --- 3. READ All Customers ---
    response = client.get("/customers/")
    assert response.status_code == 200
    # The response is paginated, so we check the 'customers' key
    assert isinstance(response.json["customers"], list)
    assert len(response.json["customers"]) > 0

    # --- 4. READ One Customer by ID ---
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 200
    assert response.json["email"] == unique_email

    # --- 5. UPDATE Customer ---
    update_data = {"first_name": "Updated"}
    response = client.put(f"/customers/{customer_id}", json=update_data, headers=headers)
    assert response.status_code == 200
    assert response.json["first_name"] == "Updated"

    # --- 6. Attempt to UPDATE another customer (Authorization Test) ---
    # Create another customer to test against
    other_customer_data = {
        "first_name": "Other",
        "last_name": "User",
        "email": f"other.user.{int(time.time())}@example.com",
        "phone_number": "555-5678",
        "password": "another-password",
    }
    res = client.post("/customers/", json=other_customer_data)
    other_customer_id = res.json["id"]

    # Use the first user's token to try to modify the second user
    response = client.put(
        f"/customers/{other_customer_id}", json={"first_name": "Hacker"}, headers=headers
    )
    assert response.status_code == 403  # Forbidden

    # --- 7. DELETE Customer ---
    response = client.delete(f"/customers/{customer_id}", headers=headers)
    assert response.status_code == 200
    assert "successfully deleted" in response.json["message"]

    # --- 8. Verify Deletion ---
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 404  # Not Found