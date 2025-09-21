import pytest
from tests.conftest import init_database, clean_database

class TestMechanicsAPI:
    """Test cases for mechanics API endpoints."""
    
    def test_get_all_mechanics_empty_database(self, client, clean_database):
        """Test GET /mechanics/ with empty database"""
        response = client.get('/mechanics/')
        assert response.status_code == 200
        data = response.get_json()
        # Response is a list, not a dict with 'mechanics' key
        assert isinstance(data, list)
        assert len(data) == 0  # Should be empty
    
    def test_get_all_mechanics_success(self, client, init_database):
        """Test GET /mechanics/ with data"""
        response = client.get('/mechanics/')
        assert response.status_code == 200
        data = response.get_json()
        # Response is a list, not a dict with 'mechanics' key
        assert isinstance(data, list)
        assert len(data) >= 2
    
    def test_create_mechanic_success(self, client, clean_database):
        """Test creating mechanic - positive case"""
        mechanic_data = {
            'name': 'Test Mechanic',
            'email': 'test.mechanic@shop.com',
            'phone': '555-0888',
            'salary': 70000.00
        }

        response = client.post('/mechanics/',
                             json=mechanic_data,
                             content_type='application/json')
        assert response.status_code == 201
    
    def test_create_mechanic_missing_required_field(self, client, clean_database):
        """Test creating mechanic with missing required field"""
        mechanic_data = {
            'email': 'test.mechanic@shop.com'
        }
        response = client.post('/mechanics/',
                             json=mechanic_data,
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_create_mechanic_invalid_email(self, client, clean_database):
        """Test creating mechanic with invalid email"""
        mechanic_data = {
            'name': 'Test Mechanic',
            'email': 'invalid-email',
            'salary': 70000.00
        }
        response = client.post('/mechanics/',
                             json=mechanic_data,
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_create_mechanic_duplicate_email(self, client, init_database):
        """Test creating mechanic with duplicate email"""
        mechanic_data = {
            'name': 'Test Mechanic',
            'email': 'mike.johnson@shop.com',
            'salary': 70000.00
        }
        response = client.post('/mechanics/',
                             json=mechanic_data,
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_get_mechanic_by_id_success(self, client, init_database):
        """Test GET /mechanics/{id} - positive case"""
        response = client.get('/mechanics/1')
        assert response.status_code == 200
    
    def test_get_mechanic_by_id_not_found(self, client, clean_database):
        """Test GET /mechanics/{id} - mechanic not found"""
        response = client.get('/mechanics/999')
        assert response.status_code == 404
    
    def test_update_mechanic_success(self, client, init_database):
        """Test PUT /mechanics/{id} - positive case"""
        update_data = {
            'name': 'Updated Mechanic',
            'salary': 80000.00
        }
        
        response = client.put('/mechanics/1',
                            json=update_data,
                            content_type='application/json')
        assert response.status_code == 200
    
    def test_update_mechanic_not_found(self, client, clean_database):
        """Test PUT /mechanics/{id} - mechanic not found"""
        update_data = {
            'name': 'Updated Mechanic'
        }
        
        response = client.put('/mechanics/999',
                            json=update_data,
                            content_type='application/json')
        assert response.status_code == 404
    
    def test_delete_mechanic_success(self, client, init_database):
        """Test DELETE /mechanics/{id} - positive case"""
        response = client.delete('/mechanics/1')
        assert response.status_code in [200, 204]  # Both are acceptable
    
    def test_delete_mechanic_not_found(self, client, clean_database):
        """Test DELETE /mechanics/{id} - mechanic not found"""
        response = client.delete('/mechanics/999')
        assert response.status_code == 404