"""
Mechanic routes for the mechanic shop API.
"""

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.extensions import db
from app.models.mechanic import Mechanic
from .schemas import mechanic_schema, mechanics_schema

# Create mechanic blueprint
mechanics_bp = Blueprint('mechanics', __name__)


@mechanics_bp.route('/', methods=['POST'])
def create_mechanic():
    """Create a new mechanic."""
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400

        # Validate and load the data
        mechanic_data = mechanic_schema.load(json_data)
        
        # Check if email already exists
        existing_mechanic = Mechanic.query.filter_by(email=mechanic_data['email']).first()
        if existing_mechanic:
            return jsonify({"error": "Email already associated with another mechanic"}), 400
        
        # Create new mechanic from the dictionary
        new_mechanic = Mechanic(**mechanic_data)
        db.session.add(new_mechanic)
        db.session.commit()

        return jsonify(mechanic_schema.dump(new_mechanic)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400


@mechanics_bp.route('/', methods=['GET'])
def get_mechanics():
    """Get all mechanics."""
    mechanics = Mechanic.query.all()
    return jsonify(mechanics_schema.dump(mechanics)), 200


@mechanics_bp.route('/<int:mechanic_id>', methods=['GET'])
def get_mechanic(mechanic_id):
    """Get a single mechanic by ID."""
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if mechanic:
        return jsonify(mechanic_schema.dump(mechanic)), 200
    
    return jsonify({"error": "Mechanic not found"}), 404


@mechanics_bp.route('/<int:mechanic_id>', methods=['PUT'])
def update_mechanic(mechanic_id):
    """Update a mechanic by ID."""
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
            
        mechanic_data = mechanic_schema.load(json_data, partial=True)
        
        # Update mechanic attributes
        for key, value in mechanic_data.items():
            setattr(mechanic, key, value)

        db.session.commit()
        return jsonify(mechanic_schema.dump(mechanic)), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400


@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'])
def delete_mechanic(mechanic_id):
    """Delete a mechanic by ID."""
    mechanic = db.session.get(Mechanic, mechanic_id)
    
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    try:
        db.session.delete(mechanic)
        db.session.commit()
        return jsonify({'message': 'Mechanic deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500