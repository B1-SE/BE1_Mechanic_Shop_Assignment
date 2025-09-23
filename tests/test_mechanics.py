"""
Test cases for the mechanics API endpoints.
"""


class TestMechanicsAPI:

    def test_get_all_mechanics_empty_database(self, client, clean_database):
        """Test GET /mechanics/ with empty database"""
        response = client.get('/mechanics/')
        assert response.status_code == 200
        data = response.get_json()
        # Response is a dict with 'mechanics' key, not a list
        assert isinstance(data, dict)
        assert 'mechanics' in data
        assert 'count' in data
        assert isinstance(data['mechanics'], list)
        assert len(data['mechanics']) == 0

    def test_get_all_mechanics_success(self, client, init_database):
        """Test GET /mechanics/ with data"""
        response = client.get('/mechanics/')
        assert response.status_code == 200
        data = response.get_json()
        # Response is a dict with 'mechanics' key, not a list
        assert isinstance(data, dict)
        assert 'mechanics' in data
        assert 'count' in data
        assert isinstance(data['mechanics'], list)
        assert len(data['mechanics']) == 2

    def test_create_mechanic_success(self, client, clean_database):
        """Test POST /mechanics/ - positive case"""
        mechanic_data = {
            'name': 'John Smith',
            'email': 'john.smith@shop.com',
            'phone': '555-0123',
            'salary': 55000
        }
        response = client.post('/mechanics/',
                             json=mechanic_data,
                             content_type='application/json')
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'John Smith'
        assert data['email'] == 'john.smith@shop.com'
        assert float(data['salary']) == 55000.0

    def test_create_mechanic_missing_required_field(self, client, clean_database):
        """Test POST /mechanics/ - missing required field"""
        mechanic_data = {
            'name': 'John Smith',
            'email': 'john.smith@shop.com'
            # Missing 'salary'
        }
        response = client.post('/mechanics/',
                             json=mechanic_data,
                             content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert 'errors' in data
        assert 'salary' in data['errors']

    def test_create_mechanic_invalid_email(self, client, clean_database):
        """Test POST /mechanics/ - invalid email format"""
        mechanic_data = {
            'name': 'John Smith',
            'email': 'invalid-email',
            'salary': 55000
        }
        response = client.post('/mechanics/',
                             json=mechanic_data,
                             content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert 'errors' in data
        assert 'email' in data['errors']

    def test_create_mechanic_duplicate_email(self, client, init_database):
        """Test POST /mechanics/ - duplicate email"""
        mechanic_data = {
            'name': 'Another Mechanic',
            'email': 'mike.johnson@shop.com',  # This email already exists
            'salary': 60000
        }
        response = client.post('/mechanics/',
                             json=mechanic_data,
                             content_type='application/json')
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_get_mechanic_by_id_success(self, client, init_database):
        """Test GET /mechanics/{id} - positive case"""
        response = client.get('/mechanics/1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == 1
        assert data['email'] == 'mike.johnson@shop.com'

    def test_get_mechanic_by_id_not_found(self, client, clean_database):
        """Test GET /mechanics/{id} - mechanic not found"""
        response = client.get('/mechanics/999')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data

    def test_update_mechanic_success(self, client, init_database):
        """Test PUT /mechanics/{id} - positive case"""
        update_data = {
            'name': 'Michael Johnson',
            'salary': 65000
        }
        response = client.put('/mechanics/1',
                            json=update_data,
                            content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == 'Michael Johnson'
        assert float(data['salary']) == 65000.0

    def test_update_mechanic_not_found(self, client, clean_database):
        """Test PUT /mechanics/{id} - mechanic not found"""
        update_data = {
            'name': 'Updated Name'
        }
        response = client.put('/mechanics/999',
                            json=update_data,
                            content_type='application/json')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data

    def test_delete_mechanic_success(self, client, init_database):
        """Test DELETE /mechanics/{id} - positive case"""
        response = client.delete('/mechanics/2')
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data

        # Verify the mechanic is actually deleted
        response = client.get('/mechanics/2')
        assert response.status_code == 404

    def test_delete_mechanic_not_found(self, client, clean_database):
        """Test DELETE /mechanics/{id} - mechanic not found"""
        response = client.delete('/mechanics/999')
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data