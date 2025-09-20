"""
Customer routes for the mechanic shop API.
"""

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.extensions import db
from app.models.customer import Customer
from app.schemas.customer import customer_schema, customers_schema

# Create customer blueprint
customers_bp = Blueprint('customers', __name__)


@customers_bp.route('/', methods=['POST'])
def create_customer():
    """Create a new customer."""
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400

        # Validate and load the data
        customer_data = customer_schema.load(json_data)
        
        # Check if email already exists
        existing_customer = Customer.query.filter_by(email=customer_data['email']).first()
        if existing_customer:
            return jsonify({"error": "Email already associated with another account"}), 400
        
        # Create new customer from the dictionary
        new_customer = Customer(**customer_data)
        db.session.add(new_customer)
        db.session.commit()

        return jsonify(customer_schema.dump(new_customer)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400


@customers_bp.route('/', methods=['GET'])
def get_customers():
    """Get all customers."""
    customers = Customer.query.all()
    return jsonify(customers_schema.dump(customers)), 200


@customers_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get a single customer by ID."""
    customer = db.session.get(Customer, customer_id)
    
    if customer:
        return jsonify(customer_schema.dump(customer)), 200
    
    return jsonify({"error": "Customer not found"}), 404


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    """Update a customer by ID."""
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
            
        customer_data = customer_schema.load(json_data, partial=True)
        
        # Update customer attributes
        for key, value in customer_data.items():
            setattr(customer, key, value)

        db.session.commit()
        return jsonify(customer_schema.dump(customer)), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    """Delete a customer by ID."""
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    try:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Customer deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500