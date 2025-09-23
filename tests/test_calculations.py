import pytest
from app import create_app

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    yield app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

class TestCalculationsAPI:
    """Test suite for calculations API endpoints"""
    
    def test_addition_basic_success(self, client):
        """Test basic addition - positive case"""
        calc_data = {'numbers': [2, 3, 5]}
        
        response = client.post('/calculations/add',
                             json=calc_data,
                             content_type='application/json')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['operation'] == 'addition'
        assert data['result'] == 10
        assert data['operands'] == [2, 3, 5]
    
    def test_addition_with_decimals(self, client):
        """Test addition with decimal numbers - positive case"""
        calc_data = {'numbers': [2.5, 3.7, 1.3]}
        
        response = client.post('/calculations/add',
                             json=calc_data,
                             content_type='application/json')
        assert response.status_code == 200
        
        data = response.get_json()
        assert abs(data['result'] - 7.5) < 0.0001
    
    def test_addition_insufficient_numbers(self, client):
        """Test addition with insufficient numbers - negative case"""
        calc_data = {'numbers': [5]}  # Only one number
        
        response = client.post('/calculations/add',
                             json=calc_data,
                             content_type='application/json')
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
    
    def test_addition_invalid_data_type(self, client):
        """Test addition with invalid data type - negative case"""
        calc_data = {'numbers': [5, 'invalid', 3]}
        
        response = client.post('/calculations/add',
                             json=calc_data,
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_addition_missing_numbers_field(self, client):
        """Test addition without numbers field - negative case"""
        calc_data = {'invalid_field': [5, 3]}
        
        response = client.post('/calculations/add',
                             json=calc_data,
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_subtraction_basic_success(self, client):
        """Test basic subtraction - positive case"""
        calc_data = {'numbers': [20, 5, 3]}
        
        response = client.post('/calculations/subtract',
                             json=calc_data,
                             content_type='application/json')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['operation'] == 'subtraction'
        assert data['result'] == 12  # 20 - 5 - 3 = 12
    
    def test_subtraction_negative_result(self, client):
        """Test subtraction resulting in negative - positive case"""
        calc_data = {'numbers': [5, 10]}
        
        response = client.post('/calculations/subtract',
                             json=calc_data,
                             content_type='application/json')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['result'] == -5
    
    def test_multiplication_basic_success(self, client):
        """Test basic multiplication - positive case"""
        calc_data = {'numbers': [4, 5, 2]}
        
        response = client.post('/calculations/multiply',
                             json=calc_data,
                             content_type='application/json')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['operation'] == 'multiplication'
        assert data['result'] == 40  # 4 × 5 × 2 = 40
    
    def test_multiplication_with_zero(self, client):
        """Test multiplication with zero - positive case"""
        calc_data = {'numbers': [5, 0, 3]}
        
        response = client.post('/calculations/multiply',
                             json=calc_data,
                             content_type='application/json')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['result'] == 0
    
    def test_division_basic_success(self, client):
        """Test basic division - positive case"""
        calc_data = {'numbers': [100, 5, 2]}
        
        response = client.post('/calculations/divide',
                             json=calc_data,
                             content_type='application/json')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['operation'] == 'division'
        assert data['result'] == 10.0  # 100 ÷ 5 ÷ 2 = 10
    
    def test_division_by_zero_error(self, client):
        """Test division by zero - negative case"""
        calc_data = {'numbers': [10, 0]}
        
        response = client.post('/calculations/divide',
                             json=calc_data,
                             content_type='application/json')
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'Division by zero' in data['error']
    
    def test_division_with_zero_in_middle(self, client):
        """Test division with zero in middle of sequence - negative case"""
        calc_data = {'numbers': [100, 5, 0, 2]}
        
        response = client.post('/calculations/divide',
                             json=calc_data,
                             content_type='application/json')
        assert response.status_code == 400
    
    def test_calculations_health_check(self, client):
        """Test calculations health endpoint - positive case"""
        response = client.get('/calculations/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['service'] == 'calculations'
        assert data['status'] == 'healthy'
        assert len(data['endpoints']) == 4