"""
Member routes - wrapping customer functionality for members
"""

from flask import Blueprint, request, jsonify
from app.extensions import db, limiter
from app.models.customer import Customer
from app.schemas.customer import customer_schema, customers_schema
from app.utils.auth import generate_token, token_required
from app.utils.util import validate_email

members_bp = Blueprint('members', __name__)

@members_bp.route('/', methods=['GET'])
@limiter.limit("100 per minute")
def get_members():
    """Get all members"""
    try:
        customers = Customer.query.all()
        result = customers_schema.dump(customers)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@members_bp.route('/', methods=['POST'])
@limiter.limit("50 per minute")
def create_member():
    """Create a new member"""
    try:
        data = request.get_json()
        
        required_fields = ['first_name', 'last_name', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        existing_customer = Customer.query.filter_by(email=data['email']).first()
        if existing_customer:
            return jsonify({'error': 'Email already exists'}), 400
        
        customer = Customer(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone_number=data.get('phone_number'),
            address=data.get('address')
        )
        customer.set_password(data['password'])
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify(customer_schema.dump(customer)), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@members_bp.route('/<int:member_id>', methods=['GET'])
@limiter.limit("100 per minute")
def get_member(member_id):
    """Get a specific member"""
    try:
        customer = db.session.get(Customer, member_id)
        if not customer:
            return jsonify({'error': 'Member not found'}), 404
        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@members_bp.route('/<int:member_id>', methods=['PUT'])
@limiter.limit("50 per minute")
@token_required
def update_member(current_customer, member_id):
    """Update a member"""
    try:
        if current_customer.id != member_id:
            return jsonify({'error': 'Unauthorized access'}), 403
            
        customer = db.session.get(Customer, member_id)
        if not customer:
            return jsonify({'error': 'Member not found'}), 404
            
        data = request.get_json()
        
        if 'first_name' in data:
            customer.first_name = data['first_name']
        if 'last_name' in data:
            customer.last_name = data['last_name']
        if 'email' in data:
            if not validate_email(data['email']):
                return jsonify({'error': 'Invalid email format'}), 400
            customer.email = data['email']
        if 'phone_number' in data:
            customer.phone_number = data['phone_number']
        if 'address' in data:
            customer.address = data['address']
        
        db.session.commit()
        return jsonify(customer_schema.dump(customer)), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@members_bp.route('/<int:member_id>', methods=['DELETE'])
@limiter.limit("50 per minute")
@token_required
def delete_member(current_customer, member_id):
    """Delete a member"""
    try:
        if current_customer.id != member_id:
            return jsonify({'error': 'Unauthorized access'}), 403
            
        customer = db.session.get(Customer, member_id)
        if not customer:
            return jsonify({'error': 'Member not found'}), 404
            
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({'message': 'Member deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@members_bp.route('/login', methods=['POST'])
@limiter.limit("50 per minute")
def member_login():
    """Member login"""
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password required'}), 400
        
        customer = Customer.query.filter_by(email=data['email']).first()
        
        if not customer or not customer.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        token = generate_token(customer.id, customer.email)
        
        return jsonify({
            'message': 'Login successful',
            'member': customer_schema.dump(customer),
            'token': token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
