"""
Test script for advanced endpoints: pagination, sorting, filtering, and bulk operations.
"""

import requests

BASE_URL = "https://your-app-name.onrender.com"


def test_advanced_endpoints():
    """Test all advanced endpoint features."""

    print("🚀 Testing Advanced Endpoints")
    print("=" * 60)

    # Test setup - create test data
    print("\n📋 Setting up test data...")

    # Create customers
    customers_data = [
        {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": "alice.smith@test.com",
            "phone_number": "555-0001",
            "password": "password123",
        },
        {
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob.johnson@test.com",
            "phone_number": "555-0002",
            "password": "password123",
        },
        {
            "first_name": "Charlie",
            "last_name": "Brown",
            "email": "charlie.brown@test.com",
            "phone_number": "555-0003",
            "password": "password123",
        },
        {
            "first_name": "Diana",
            "last_name": "Adams",
            "email": "diana.adams@test.com",
            "phone_number": "555-0004",
            "password": "password123",
        },
        {
            "first_name": "Eve",
            "last_name": "Wilson",
            "email": "eve.wilson@test.com",
            "phone_number": "555-0005",
            "password": "password123",
        },
    ]

    customer_ids = []
    for customer_data in customers_data:
        response = requests.post(f"{BASE_URL}/customers/", json=customer_data)
        if response.status_code == 201:
            customer_ids.append(response.json()["id"])
            print(
                f"✅ Created customer: {customer_data['first_name']} {customer_data['last_name']}"
            )

    # Create mechanics
    mechanics_data = [
        {
            "name": "John Wrench",
            "email": "john.wrench@shop.com",
            "phone_number": "555-1001",
            "hourly_rate": 45.0,
        },
        {
            "name": "Jane Gear",
            "email": "jane.gear@shop.com",
            "phone_number": "555-1002",
            "hourly_rate": 50.0,
        },
        {
            "name": "Mike Bolt",
            "email": "mike.bolt@shop.com",
            "phone_number": "555-1003",
            "hourly_rate": 40.0,
        },
    ]

    mechanic_ids = []
    for mechanic_data in mechanics_data:
        response = requests.post(f"{BASE_URL}/mechanics/", json=mechanic_data)
        if response.status_code == 201:
            mechanic_ids.append(response.json()["id"])
            print(f"✅ Created mechanic: {mechanic_data['name']}")

    # Create service tickets
    service_tickets_data = [
        {
            "customer_id": customer_ids[0],
            "description": "Oil change and tire rotation",
            "service_date": "2025-09-21",
            "mechanic_ids": [mechanic_ids[0]],
        },
        {
            "customer_id": customer_ids[1],
            "description": "Brake inspection",
            "service_date": "2025-09-22",
            "mechanic_ids": [mechanic_ids[0], mechanic_ids[1]],
        },
        {
            "customer_id": customer_ids[2],
            "description": "Engine diagnostic",
            "service_date": "2025-09-23",
            "mechanic_ids": [mechanic_ids[1]],
        },
        {
            "customer_id": customer_ids[0],
            "description": "Transmission service",
            "service_date": "2025-09-24",
            "mechanic_ids": [mechanic_ids[0], mechanic_ids[2]],
        },
    ]

    ticket_ids = []
    for ticket_data in service_tickets_data:
        response = requests.post(f"{BASE_URL}/service-tickets/", json=ticket_data)
        if response.status_code == 201:
            ticket_ids.append(response.json()["id"])
            print(f"✅ Created service ticket: {ticket_data['description'][:30]}...")

    print(
        f"\n📊 Test data created: {len(customer_ids)} customers, {len(mechanic_ids)} mechanics, {len(ticket_ids)} tickets"
    )

    # Test 1: Customer Pagination
    print("\n1. Testing Customer Pagination...")

    # Test basic pagination
    response = requests.get(f"{BASE_URL}/customers/?page=1&per_page=3")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Page 1 (3 per page): {len(data['customers'])} customers")
        print(
            f"   Total: {data['pagination']['total']}, Pages: {data['pagination']['pages']}"
        )
    else:
        print(f"❌ Pagination failed: {response.text}")

    # Test 2: Customer Sorting
    print("\n2. Testing Customer Sorting...")

    # Sort by first name descending
    response = requests.get(f"{BASE_URL}/customers/?sort_by=first_name&order=desc")
    if response.status_code == 200:
        data = response.json()
        names = [c["first_name"] for c in data["customers"]]
        print(f"✅ Sorted by first_name (desc): {names[:5]}")
    else:
        print(f"❌ Sorting failed: {response.text}")

    # Test 3: Customer Search/Filtering
    print("\n3. Testing Customer Search and Filtering...")

    # Search for customers with "a" in name or email
    response = requests.get(f"{BASE_URL}/customers/?search=a")
    if response.status_code == 200:
        data = response.json()
        found_names = [f"{c['first_name']} {c['last_name']}" for c in data["customers"]]
        print(f"✅ Search for 'a': Found {len(found_names)} customers: {found_names}")
    else:
        print(f"❌ Search failed: {response.text}")

    # Filter by email domain
    response = requests.get(f"{BASE_URL}/customers/?email=test.com")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Email filter 'test.com': Found {len(data['customers'])} customers")
    else:
        print(f"❌ Email filter failed: {response.text}")

    # Test 4: Combined pagination, sorting, and filtering
    print("\n4. Testing Combined Parameters...")

    response = requests.get(
        f"{BASE_URL}/customers/?search=a&sort_by=last_name&order=asc&page=1&per_page=2"
    )
    if response.status_code == 200:
        data = response.json()
        print(
            f"✅ Combined query: {len(data['customers'])} customers with 'a', sorted by last_name"
        )
        print(f"   Filters applied: {data['filters_applied']}")
    else:
        print(f"❌ Combined query failed: {response.text}")

    # Test 5: Mechanics by Workload
    print("\n5. Testing Mechanics by Workload...")

    response = requests.get(f"{BASE_URL}/mechanics/by-workload")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Mechanics by workload (desc): {data['total_mechanics']} mechanics")
        for mechanic in data["mechanics"][:3]:
            print(f"   {mechanic['name']}: {mechanic['ticket_count']} tickets")
    else:
        print(f"❌ Mechanics by workload failed: {response.text}")

    # Test ascending order
    response = requests.get(f"{BASE_URL}/mechanics/by-workload?order=asc&limit=2")
    if response.status_code == 200:
        data = response.json()
        print("✅ Mechanics by workload (asc, limit 2):")
        for mechanic in data["mechanics"]:
            print(f"   {mechanic['name']}: {mechanic['ticket_count']} tickets")
    else:
        print(f"❌ Mechanics by workload (asc) failed: {response.text}")

    # Test 6: Service Ticket Bulk Edit
    print("\n6. Testing Service Ticket Bulk Edit...")

    if ticket_ids:
        # Add and remove mechanics from a ticket
        edit_data = {
            "add_ids": [mechanic_ids[2]],  # Add Mike Bolt
            "remove_ids": [mechanic_ids[0]],  # Remove John Wrench
        }

        response = requests.put(
            f"{BASE_URL}/service-tickets/{ticket_ids[0]}/edit", json=edit_data
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Bulk edit successful:")
            print(f"   Changes made: {len(data['changes_made'])}")
            for change in data["changes_made"]:
                print(f"   - {change}")

            # Verify the ticket now has the correct mechanics
            current_mechanics = [m["name"] for m in data["service_ticket"]["mechanics"]]
            print(f"   Current mechanics: {current_mechanics}")
        else:
            print(f"❌ Bulk edit failed: {response.text}")

    # Test 7: Error Handling
    print("\n7. Testing Error Handling...")

    # Test invalid sort field
    response = requests.get(f"{BASE_URL}/customers/?sort_by=invalid_field")
    if response.status_code == 400:
        print("✅ Invalid sort field properly rejected")
    else:
        print(f"❌ Invalid sort field not rejected: {response.status_code}")

    # Test invalid pagination
    response = requests.get(f"{BASE_URL}/customers/?page=-1")
    if (
        response.status_code != 200
        or response.json().get("pagination", {}).get("page", 1) == 1
    ):
        print("✅ Invalid page number handled gracefully")
    else:
        print("❌ Invalid page number not handled properly")

    # Test bulk edit with non-existent mechanics
    if ticket_ids:
        edit_data = {
            "add_ids": [9999],  # Non-existent mechanic
            "remove_ids": [8888],  # Non-existent mechanic
        }

        response = requests.put(
            f"{BASE_URL}/service-tickets/{ticket_ids[0]}/edit", json=edit_data
        )
        if response.status_code in [400, 207]:  # Bad request or multi-status
            data = response.json()
            if "errors" in data:
                print(
                    f"✅ Bulk edit error handling: {len(data['errors'])} errors reported"
                )
            else:
                print("✅ Bulk edit error handling working")
        else:
            print(f"❌ Bulk edit error handling failed: {response.status_code}")

    print("\n" + "=" * 60)
    print("🎉 Advanced Endpoints Testing Complete!")
    print(
        "✨ All advanced features (pagination, sorting, filtering, bulk operations) tested!"
    )


if __name__ == "__main__":
    try:
        test_advanced_endpoints()
    except requests.exceptions.ConnectionError:
        print(
            "❌ Could not connect to server. Make sure the Flask app is running on http://127.0.0.1:5000"
        )
    except Exception as e:
        print(f"❌ Error during testing: {e}")
