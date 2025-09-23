"""
Service ticket tests for the mechanic shop application.
"""



class TestServiceTicketAPI:
    """Test service ticket API endpoints"""
    
    def test_create_service_ticket_success(self, client, init_database):
        """Test POST /service-tickets/ - success case"""
        service_ticket_data = {
            'customer_id': 1,
            'mechanic_id': 1,
            'vehicle_info': '2021 Honda Civic',
            'description': 'Oil change required',
            'estimated_cost': 50.00
        }
        
        response = client.post('/service-tickets/',
                             json=service_ticket_data,
                             content_type='application/json')
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['customer_id'] == 1
        assert data['mechanic_id'] == 1
        assert data['vehicle_info'] == '2021 Honda Civic'
        assert data['status'] == 'pending'
    
    def test_get_all_service_tickets_success(self, client, init_database):
        """Test GET /service-tickets/ - success case"""
        response = client.get('/service-tickets/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'service_tickets' in data
        assert len(data['service_tickets']) >= 0
    
    def test_get_service_ticket_by_id_success(self, client, init_database):
        """Test GET /service-tickets/{id} - success case"""
        # First create a service ticket to ensure it exists
        service_ticket_data = {
            'customer_id': 1,
            'mechanic_id': 1,
            'vehicle_info': '2021 Honda Civic',
            'description': 'Test service',
            'estimated_cost': 100.00
        }
        
        create_response = client.post('/service-tickets/',
                                    json=service_ticket_data,
                                    content_type='application/json')
        assert create_response.status_code == 201
        
        created_ticket = create_response.get_json()
        ticket_id = created_ticket['id']
        
        # Now test getting the created ticket
        response = client.get(f'/service-tickets/{ticket_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == ticket_id
    
    def test_get_service_ticket_by_id_not_found(self, client, init_database):
        """Test GET /service-tickets/{id} - not found"""
        response = client.get('/service-tickets/999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data