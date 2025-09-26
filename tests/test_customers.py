"""
Unit tests for the Inventory API endpoints.
"""
import unittest
from unittest.mock import patch
from tests.test_base import BaseTestCase
from app.models.inventory import Inventory
from app.extensions import db


class TestInventoryAPI(BaseTestCase):
    """Test cases for the Inventory API endpoints."""

    def test_get_all_inventory_success(self):
        """Test getting all inventory items - positive case"""
        item = Inventory(name="Test Part", price=10.0)
        db.session.add(item)
        db.session.commit()

        response = self.client.get("/inventory/")
        self.assertEqual(response.status_code, 200)
        data = self.get_json_response(response)
        self.assertEqual(len(data["items"]), 1)
        self.assertEqual(data["items"][0]["name"], "Test Part")

    def test_get_inventory_by_id_success(self):
        """Test getting inventory item by ID - positive case"""
        item = Inventory(id=1, name="Test Part", price=10.0)
        db.session.add(item)
        db.session.commit()

        response = self.client.get("/inventory/1")
        self.assertEqual(response.status_code, 200)
        data = self.get_json_response(response)
        self.assertEqual(data["name"], "Test Part")

    def test_get_inventory_by_id_not_found(self):
        """Test getting non-existent inventory item - negative case"""
        response = self.client.get("/inventory/999")
        self.assertEqual(response.status_code, 404)

    @patch('app.blueprints.inventory.routes.mechanic_token_required', lambda f: lambda *args, **kwargs: f(mechanic_id=1, *args, **kwargs))
    def test_create_inventory_item_success(self):
        """Test creating inventory item - positive case"""
        item_data = {
            "name": "Air Filter",
            "price": 45.99,
        }
        response = self.client.post(
            "/inventory/", json=item_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = self.get_json_response(response)
        self.assertEqual(data["name"], "Air Filter")

    @patch('app.blueprints.inventory.routes.mechanic_token_required', lambda f: lambda *args, **kwargs: f(mechanic_id=1, *args, **kwargs))
    def test_create_inventory_item_missing_required_field(self):
        """Test creating inventory item without required field - negative case"""
        item_data = {"name": "Test Item"} # Missing price
        response = self.client.post(
            "/inventory/", json=item_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)

    @patch('app.blueprints.inventory.routes.mechanic_token_required', lambda f: lambda *args, **kwargs: f(mechanic_id=1, *args, **kwargs))
    def test_create_inventory_item_duplicate_name(self):
        """Test creating inventory item with a duplicate name."""
        item = Inventory(name="Existing Part", price=10.0)
        db.session.add(item)
        db.session.commit()
        
        item_data = {"name": "Existing Part", "price": 20.0}
        response = self.client.post(
            "/inventory/", json=item_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 409)

    @patch('app.blueprints.inventory.routes.mechanic_token_required', lambda f: lambda *args, **kwargs: f(mechanic_id=1, *args, **kwargs))
    def test_update_inventory_item_success(self):
        """Test updating inventory item - positive case"""
        item = Inventory(id=1, name="Old Name", price=10.0)
        db.session.add(item)
        db.session.commit()

        update_data = {"name": "New Name", "price": 29.99}
        response = self.client.put(
            "/inventory/1", json=update_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = self.get_json_response(response)
        self.assertEqual(data["name"], "New Name")
        self.assertEqual(data["price"], 29.99)

    @patch('app.blueprints.inventory.routes.mechanic_token_required', lambda f: lambda *args, **kwargs: f(mechanic_id=1, *args, **kwargs))
    def test_update_inventory_item_not_found(self):
        """Test updating non-existent inventory item - negative case"""
        update_data = {"name": "New Name"}
        response = self.client.put(
            "/inventory/999", json=update_data, content_type="application/json"
        )
        self.assertEqual(response.status_code, 404)

    @patch('app.blueprints.inventory.routes.mechanic_token_required', lambda f: lambda *args, **kwargs: f(mechanic_id=1, *args, **kwargs))
    def test_delete_inventory_item_success(self):
        """Test deleting inventory item - positive case"""
        item = Inventory(id=1, name="To Delete", price=10.0)
        db.session.add(item)
        db.session.commit()

        response = self.client.delete("/inventory/1")
        self.assertEqual(response.status_code, 200)

        # Verify deletion
        deleted_item = db.session.get(Inventory, 1)
        self.assertIsNone(deleted_item)

    @patch('app.blueprints.inventory.routes.mechanic_token_required', lambda f: lambda *args, **kwargs: f(mechanic_id=1, *args, **kwargs))
    def test_delete_inventory_item_not_found(self):
        """Test deleting non-existent inventory item - negative case"""
        response = self.client.delete("/inventory/999")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
