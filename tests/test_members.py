
class TestMembersAPI:
    """Test cases for members API endpoints."""

    def _login_and_get_token(self, client, email='john.doe@test.com', password='password123'):
        """Helper method to login and get auth token"""
        login_data = {
            'email': email,
            'password': password
        }
        # The /members/login endpoint should be an alias for /customers/login
        response = client.post('/members/login',
                             json=login_data,
                             content_type='application/json')
        if response.status_code == 200:
            return response.get_json()['token']
        return None

    def test_get_all_members_empty_database(self, client, clean_database):
        """Test GET /members/ with empty database"""
        response = client.get('/members/')
        assert response.status_code == 200
        data = response.get_json()
        # The /members endpoint is an alias for /customers
        assert 'customers' in data
        assert len(data['customers']) == 0

    def test_get_all_members_success(self, client, init_database):
        """Test GET /members/ with data"""
        response = client.get('/members/')
        assert response.status_code == 200
        data = response.get_json()
        assert 'customers' in data
        assert len(data['customers']) >= 2

    def test_create_member_success(self, client, clean_database):
        """Test creating a new member (customer) via POST /members/"""
        member_data = {
            'first_name': 'Test',
            'last_name': 'Member',
            'email': 'test.member@test.com',
            'phone_number': '555-1000',
            'password': 'testpassword'
        }
        response = client.post('/members/',
                             json=member_data,
                             content_type='application/json')
        assert response.status_code == 201
        data = response.get_json()
        assert data['email'] == 'test.member@test.com'

    def test_create_member_duplicate_email(self, client, init_database):
        """Test creating a member with a duplicate email"""
        member_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@test.com', # This email exists in init_database
            'password': 'newpassword'
        }
        response = client.post('/members/',
                             json=member_data,
                             content_type='application/json')
        assert response.status_code == 400

    def test_get_member_by_id_success(self, client, init_database):
        """Test GET /members/{id} - positive case"""
        response = client.get('/members/1')
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == 1
        assert data['email'] == 'john.doe@test.com'

    def test_get_member_by_id_not_found(self, client, clean_database):
        """Test GET /members/{id} - member not found"""
        response = client.get('/members/999')
        assert response.status_code == 404

    def test_member_login_success(self, client, init_database):
        """Test successful member login via /members/login"""
        login_data = {
            'email': 'john.doe@test.com',
            'password': 'password123'
        }
        response = client.post('/members/login',
                             json=login_data,
                             content_type='application/json')
        assert response.status_code == 200
        data = response.get_json()
        assert 'token' in data
        assert 'customer' in data
        assert data['customer']['email'] == 'john.doe@test.com'

    def test_member_login_invalid_credentials(self, client, init_database):
        """Test member login with invalid credentials"""
        login_data = {
            'email': 'john.doe@test.com',
            'password': 'wrongpassword'
        }
        response = client.post('/members/login',
                             json=login_data,
                             content_type='application/json')
        assert response.status_code == 401

    def test_update_member_success(self, client, init_database):
        """Test PUT /members/{id} - positive case"""
        # Get auth token
        token = self._login_and_get_token(client)
        assert token is not None, "Failed to get auth token"

        update_data = {
            'first_name': 'Johnathan'
        }

        headers = {'Authorization': f'Bearer {token}'}
        response = client.put('/members/1',
                            json=update_data,
                            content_type='application/json',
                            headers=headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data['first_name'] == 'Johnathan'

    def test_update_other_member_unauthorized(self, client, init_database):
        """Test PUT /members/{id} - trying to update a different member"""
        # Login as customer 1
        token = self._login_and_get_token(client, email='john.doe@test.com')
        assert token is not None, "Failed to get auth token"

        update_data = {'first_name': 'Unauthorized Update'}
        headers = {'Authorization': f'Bearer {token}'}
        # Try to update customer 2 (should be forbidden)
        response = client.put('/members/2',
                            json=update_data,
                            content_type='application/json',
                            headers=headers)
        assert response.status_code == 403

    def test_delete_member_success(self, client, init_database):
        """Test DELETE /members/{id} - positive case"""
        # Get auth token
        token = self._login_and_get_token(client, email='jane.smith@test.com', password='password456')
        assert token is not None, "Failed to get auth token"

        headers = {'Authorization': f'Bearer {token}'}
        # Delete customer 2
        response = client.delete('/members/2', headers=headers)
        assert response.status_code == 200

        # Verify deletion
        response = client.get('/members/2', headers=headers)
        assert response.status_code == 404
        response = client.delete('/members/1', headers=headers)
        assert response.status_code in [200, 204, 404, 401]  # May not exist or need auth