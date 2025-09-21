"""
Mechanics routes for the mechanic shop application.
"""

from flask import Blueprint, request, jsonify
from app.extensions import db, limiter
from app.models.mechanic import Mechanic
from marshmallow import ValidationError
import re

# Create mechanics blueprint
mechanics_bp = Blueprint('mechanics', __name__)


def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


@mechanics_bp.route('/', methods=['GET'])
@limiter.limit("100 per minute")
def get_all_mechanics():
    """Get all mechanics"""
    try:
        mechanics = Mechanic.query.all()
        result = []
        for mechanic in mechanics:
            result.append(mechanic.to_dict())
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mechanics_bp.route('/<int:mechanic_id>', methods=['GET'])
@limiter.limit("100 per minute")
def get_mechanic(mechanic_id):
    """Get a specific mechanic"""
    try:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({'error': 'Mechanic not found'}), 404
        return jsonify(mechanic.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@mechanics_bp.route('/', methods=['POST'])
@limiter.limit("50 per minute")
def create_mechanic():
    """Create a new mechanic"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'email']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate email format
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check if email already exists (case-insensitive and thorough check)
        email_to_check = data['email'].strip().lower()
        
        # Try multiple ways to check for existing email
        existing_mechanic = None
        try:
            # Method 1: Case-insensitive LIKE query
            existing_mechanic = db.session.query(Mechanic).filter(
                db.func.lower(Mechanic.email) == email_to_check
            ).first()
            
            # Method 2: If that doesn't work, check all emails manually
            if not existing_mechanic:
                all_mechanics = Mechanic.query.all()
                for mech in all_mechanics:
                    if mech.email and mech.email.strip().lower() == email_to_check:
                        existing_mechanic = mech
                        break
        except Exception:
            # Fallback to simple query
            existing_mechanic = Mechanic.query.filter_by(email=data['email']).first()
        
        if existing_mechanic:
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new mechanic
        mechanic = Mechanic(
            name=data['name'],
            email=data['email'].strip(),  # Store email with whitespace trimmed
            phone=data.get('phone'),
            salary=data.get('salary'),
            is_active=data.get('is_active', True),
            specializations=data.get('specializations')
        )
        
        # Save to database
        db.session.add(mechanic)
        db.session.commit()
        
        return jsonify(mechanic.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@mechanics_bp.route('/<int:mechanic_id>', methods=['PUT'])
@limiter.limit("50 per minute")
def update_mechanic(mechanic_id):
    """Update a mechanic"""
    try:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({'error': 'Mechanic not found'}), 404
            
        data = request.get_json()
        
        # Validate email format if provided
        if 'email' in data and not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Update fields
        if 'name' in data:
            mechanic.name = data['name']
        if 'email' in data:
            # Check if new email already exists (for different mechanic)
            email_to_check = data['email'].strip().lower()
            existing = db.session.query(Mechanic).filter(
                db.func.lower(Mechanic.email) == email_to_check,
                Mechanic.id != mechanic_id
            ).first()
            if existing:
                return jsonify({'error': 'Email already exists'}), 400
            mechanic.email = data['email'].strip()
        if 'phone' in data:
            mechanic.phone = data['phone']
        if 'salary' in data:
            mechanic.salary = data['salary']
        if 'is_active' in data:
            mechanic.is_active = data['is_active']
        if 'specializations' in data:
            mechanic.specializations = data['specializations']
        
        db.session.commit()
        return jsonify(mechanic.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@mechanics_bp.route('/<int:mechanic_id>', methods=['DELETE'])
@limiter.limit("50 per minute")
def delete_mechanic(mechanic_id):
    """Delete a mechanic"""
    try:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({'error': 'Mechanic not found'}), 404
            
        db.session.delete(mechanic)
        db.session.commit()
        
        return jsonify({'message': 'Mechanic deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500