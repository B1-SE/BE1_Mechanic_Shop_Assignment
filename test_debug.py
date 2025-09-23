#!/usr/bin/env python3

from app import create_app


def test_routes():
    app = create_app()

    print("📍 All registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.methods} {rule.rule} -> {rule.endpoint}")

    print("\n🧪 Testing customer endpoints:")
    with app.test_client() as client:
        # Test GET /customers/
        response = client.get("/customers/")
        print(f"GET /customers/ - Status: {response.status_code}")
        print(f"Response: {response.get_json()}")

        # Test POST /customers/
        test_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com",
            "password": "testpass",
        }
        response = client.post("/customers/", json=test_data)
        print(f"POST /customers/ - Status: {response.status_code}")
        print(f"Response: {response.get_json()}")


if __name__ == "__main__":
    test_routes()
