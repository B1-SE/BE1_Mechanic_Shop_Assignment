"""
Customer routes for the mechanic shop application.
"""

from flask import Blueprint, request, jsonify
from app.extensions import db, limiter
from app.models.customer import Customer
from app.schemas.customer import customer_schema, customers_schema
from app.utils.auth import generate_token, token_required, check_customer_ownership
from marshmallow import ValidationError
from werkzeug.security import check_password_hash
import re

# Create customers blueprint
customers_bp = Blueprint('customers', __name__)


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@customers_bp.route('/', methods=['GET'])
@limiter.limit("100 per minute")
def get_all_customers():
    """Get all customers"""
    try:
        customers = Customer.query.all()
        result = []
        for customer in customers:
            result.append(customer.to_dict())
        
        return jsonify({
            'customers': result,
            'count': len(result)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/<int:customer_id>', methods=['GET'])
@limiter.limit("100 per minute")
def get_customer(customer_id):
    """Get a specific customer"""
    try:
        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        return jsonify(customer.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/', methods=['POST'])
@limiter.limit("50 per minute")
def create_customer():
    """Create a new customer"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if email already exists
        existing_customer = Customer.query.filter_by(email=data['email']).first()
        if existing_customer:
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new customer
        customer = Customer(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone_number=data.get('phone_number'),
            address=data.get('address')
        )
        
        # Set password if provided
        if 'password' in data:
            customer.set_password(data['password'])
        
        # Save to database
        db.session.add(customer)
        db.session.commit()
        
        return jsonify(customer.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@limiter.limit("50 per minute")
@token_required
@check_customer_ownership('customer_id')
def update_customer(current_customer, customer_id):
    """Update a customer (requires authentication)"""
    try:
        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
            
        data = request.get_json()
        
        # Validate email format if provided
        if 'email' in data and not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Update fields
        if 'first_name' in data:
            customer.first_name = data['first_name']
        if 'last_name' in data:
            customer.last_name = data['last_name']
        if 'email' in data:
            # Check if new email already exists (for different customer)
            existing = Customer.query.filter_by(email=data['email']).first()
            if existing and existing.id != customer_id:
                return jsonify({'error': 'Email already exists'}), 400
            customer.email = data['email']
        if 'phone_number' in data:
            customer.phone_number = data['phone_number']
        if 'address' in data:
            customer.address = data['address']
        if 'password' in data:
            customer.set_password(data['password'])
        
        db.session.commit()
        return jsonify(customer.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@limiter.limit("50 per minute")
@token_required
@check_customer_ownership('customer_id')
def delete_customer(current_customer, customer_id):
    """Delete a customer (requires authentication)"""
    try:
        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
            
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({'message': 'Customer deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@customers_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Customer login"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password required'}), 400
        
        customer = Customer.query.filter_by(email=data['email']).first()
        
        if not customer or not customer.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate proper JWT token
        token = generate_token(customer.id, customer.email)
        
        return jsonify({
            'message': 'Login successful',
            'customer': customer.to_dict(),
            'token': token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500