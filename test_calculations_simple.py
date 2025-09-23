"""Simple test for calculations endpoints"""

import requests


def test_calculations_endpoints():
    """Test calculations endpoints manually"""
    base_url = "http://localhost:5001"  # Use port 5001

    print("🧮 Testing Calculations API Endpoints...")

    # Test Addition
    print("\n➕ Testing Addition:")
    response = requests.post(
        f"{base_url}/calculations/add", json={"numbers": [2, 3, 5]}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Addition: {data['calculation']}")
        print(f"   Result: {data['result']}")
    else:
        print(f"❌ Addition failed: {response.status_code}")

    # Test Subtraction
    print("\n➖ Testing Subtraction:")
    response = requests.post(
        f"{base_url}/calculations/subtract", json={"numbers": [20, 5, 3]}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Subtraction: {data['calculation']}")
        print(f"   Result: {data['result']}")
    else:
        print(f"❌ Subtraction failed: {response.status_code}")

    # Test Multiplication
    print("\n✖️ Testing Multiplication:")
    response = requests.post(
        f"{base_url}/calculations/multiply", json={"numbers": [4, 5, 2]}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Multiplication: {data['calculation']}")
        print(f"   Result: {data['result']}")
    else:
        print(f"❌ Multiplication failed: {response.status_code}")

    # Test Division
    print("\n➗ Testing Division:")
    response = requests.post(
        f"{base_url}/calculations/divide", json={"numbers": [100, 5, 2]}
    )
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Division: {data['calculation']}")
        print(f"   Result: {data['result']}")
    else:
        print(f"❌ Division failed: {response.status_code}")

    # Test Division by Zero
    print("\n🚫 Testing Division by Zero:")
    response = requests.post(
        f"{base_url}/calculations/divide", json={"numbers": [10, 0]}
    )
    if response.status_code == 400:
        data = response.json()
        print(f"✅ Division by zero properly handled: {data['error']}")
    else:
        print(f"❌ Division by zero test failed: {response.status_code}")

    # Test Health Check
    print("\n❤️ Testing Health Check:")
    response = requests.get(f"{base_url}/calculations/health")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Health check: {data['status']}")
        print(f"   Available endpoints: {len(data['endpoints'])}")
    else:
        print(f"❌ Health check failed: {response.status_code}")


if __name__ == "__main__":
    test_calculations_endpoints()
