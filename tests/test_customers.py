import pytest
from tests.conftest import init_database, clean_database

class TestCustomersAPI:
    """Test cases for customers API endpoints."""
    
    def test_get_all_customers_empty_database(self, client, clean_database):
        """Test GET /customers/ with empty database"""
        response = client.get('/customers/')
        assert response.status_code == 200
        data = response.get_json()
        assert 'customers' in data
        # Empty test should have no customers
        assert len(data['customers']) == 0
    
    def test_get_all_customers_success(self, client, init_database):
        """Test GET /customers/ with data"""
        response = client.get('/customers/')
        assert response.status_code == 200
        data = response.get_json()
        assert 'customers' in data
        assert len(data['customers']) >= 2
    
    def test_create_customer_success(self, client, clean_database):
        """Test creating customer - positive case"""
        customer_data = {
            'first_name': 'Test',
            'last_name': 'Customer',
            'email': 'test.customer@test.com',
            'phone_number': '555-0999',
            'address': '999 Test St',
            'password': 'test123'
        }

        response = client.post('/customers/',
                             json=customer_data,
                             content_type='application/json')
        assert response.status_code == 201
    
    def test_create_customer_missing_required_field(self, client, clean_database):
        """Test creating customer with missing required field"""
        customer_data = {
            'last_name': 'Customer',
            'email': 'test.customer@test.com'
        }
        response = client.post('/customers/',
                             json=customer_data,
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_create_customer_invalid_email(self, client, clean_database):
        """Test creating customer with invalid email"""
        customer_data = {
            'first_name': 'Test',
            'last_name': 'Customer',
            'email': 'invalid-email',
            'password': 'test123'
        }
        response = client.post('/customers/',
                             json=customer_data,
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_create_customer_duplicate_email(self, client, init_database):
        """Test creating customer with duplicate email"""
        customer_data = {
            'first_name': 'Test',
            'last_name': 'Customer',
            'email': 'john.doe@test.com',
            'password': 'test123'
        }
        response = client.post('/customers/',
                             json=customer_data,
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_get_customer_by_id_success(self, client, init_database):
        """Test GET /customers/{id} - positive case"""
        response = client.get('/customers/1')
        assert response.status_code == 200
    
    def test_get_customer_by_id_not_found(self, client, clean_database):
        """Test GET /customers/{id} - customer not found"""
        response = client.get('/customers/999')
        assert response.status_code == 404
    
    def _login_and_get_token(self, client, email='john.doe@test.com', password='password123'):
        """Helper method to login and get auth token"""
        login_data = {
            'email': email,
            'password': password
        }
        response = client.post('/customers/login',
                             json=login_data,
                             content_type='application/json')
        if response.status_code == 200:
            return response.get_json()['token']
        return None
    
    def test_update_customer_success(self, client, init_database):
        """Test PUT /customers/{id} - positive case"""
        # Login to get token
        token = self._login_and_get_token(client)
        assert token is not None, "Failed to get auth token"
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        headers = {'Authorization': f'Bearer {token}'}
        response = client.put('/customers/1',
                            json=update_data,
                            content_type='application/json',
                            headers=headers)
        assert response.status_code == 200
    
    def test_update_customer_not_found(self, client, init_database):
        """Test PUT /customers/{id} - customer not found"""
        # Login to get token
        token = self._login_and_get_token(client)
        assert token is not None, "Failed to get auth token"
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        headers = {'Authorization': f'Bearer {token}'}
        response = client.put('/customers/999',
                            json=update_data,
                            content_type='application/json',
                            headers=headers) # This will be forbidden before it's not found
        assert response.status_code == 403
    
    def test_update_customer_unauthorized(self, client, init_database):
        """Test PUT /customers/{id} - trying to update different customer"""
        # Login as customer 1
        token = self._login_and_get_token(client)
        assert token is not None, "Failed to get auth token"
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        headers = {'Authorization': f'Bearer {token}'}
        # Try to update customer 2 (should fail)
        response = client.put('/customers/2',
                            json=update_data,
                            content_type='application/json',
                            headers=headers)
        assert response.status_code == 403
    
    def test_delete_customer_success(self, client, init_database):
        """Test DELETE /customers/{id} - positive case"""
        # Login to get token
        token = self._login_and_get_token(client)
        assert token is not None, "Failed to get auth token"
        
        headers = {'Authorization': f'Bearer {token}'}
        response = client.delete('/customers/1', headers=headers)
        assert response.status_code == 200 # The API returns 200 with a message
    
    def test_delete_customer_not_found(self, client, init_database):
        """Test DELETE /customers/{id} - customer not found"""
        # Login to get token
        token = self._login_and_get_token(client)
        assert token is not None, "Failed to get auth token"
        
        headers = {'Authorization': f'Bearer {token}'}
        response = client.delete('/customers/999', headers=headers)
        assert response.status_code == 403 # This will be forbidden before it's not found
    
    def test_delete_customer_unauthorized(self, client, init_database):
        """Test DELETE /customers/{id} - trying to delete different customer"""
        # Login as customer 1
        token = self._login_and_get_token(client)
        assert token is not None, "Failed to get auth token"
        
        headers = {'Authorization': f'Bearer {token}'}
        # Try to delete customer 2 (should fail)
        response = client.delete('/customers/2', headers=headers)
        assert response.status_code == 403
    
    def test_login_success(self, client, init_database):
        """Test successful customer login"""
        login_data = {
            'email': 'john.doe@test.com',
            'password': 'password123'
        }
        response = client.post('/customers/login',
                             json=login_data,
                             content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert 'token' in data
        assert 'customer' in data
    
    def test_login_invalid_credentials(self, client, init_database):
        """Test login with invalid credentials"""
        login_data = {
            'email': 'john.doe@test.com',
            'password': 'wrongpassword'
        }
        response = client.post('/customers/login',
                             json=login_data,
                             content_type='application/json')
        assert response.status_code == 401