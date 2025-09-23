"""
Mechanic routes for the mechanic shop API.
"""

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.extensions import db, cache, limiter
from app.models.mechanic import Mechanic
from .schemas import mechanic_schema, mechanics_schema

# Create mechanic blueprint
mechanics_bp = Blueprint('mechanics', __name__)


@mechanics_bp.route('/', methods=['POST'])
@limiter.limit("10 per minute")  # Rate limit mechanic creation
def create_mechanic():
    """
    Create a new mechanic.
    
    Rate Limited: 10 requests per minute per IP address
    WHY: Prevents spam mechanic account creation and protects against
    automated attacks that could flood the system with fake mechanics.
    """
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

        # Clear the cached mechanics list since we added a new mechanic
        cache.delete('all_mechanics')

        return jsonify(mechanic_schema.dump(new_mechanic)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400


@mechanics_bp.route('/by-workload', methods=['GET'])
def get_mechanics_by_workload():
    """
    Get mechanics ordered by the number of service tickets they've worked on.
    
    Query Parameters:
    - order: Sort order (asc, desc) (default: desc - most tickets first)
    - limit: Maximum number of mechanics to return (default: all)
    
    Returns mechanics with their ticket counts, sorted by workload.
    This endpoint is useful for:
    - Identifying the most experienced mechanics
    - Load balancing ticket assignments
    - Performance reviews and workload analysis
    """
    try:
        
        # Get query parameters
        order = request.args.get('order', 'desc').lower()
        limit = request.args.get('limit', type=int)
        
        # Validate order parameter
        if order not in ['asc', 'desc']:
            return jsonify({
                'error': 'Invalid order',
                'message': 'order must be "asc" or "desc"'
            }), 400
        
        # Build subquery to count tickets per mechanic
        # Using a subquery approach for better compatibility
        
        # Get all mechanics first
        all_mechanics = Mechanic.query.all()
        
        # Count tickets for each mechanic
        mechanics_with_workload = []
        for mechanic in all_mechanics:
            # Count tickets for this mechanic using the relationship
            ticket_count = len(mechanic.service_tickets)
            
            mechanic_data = mechanic_schema.dump(mechanic)
            mechanic_data['ticket_count'] = ticket_count
            mechanics_with_workload.append(mechanic_data)
        
        # Sort by ticket count
        if order == 'desc':
            mechanics_with_workload.sort(key=lambda x: (-x['ticket_count'], x['name']))
        else:
            mechanics_with_workload.sort(key=lambda x: (x['ticket_count'], x['name']))
        
        # Apply limit if specified
        if limit and limit > 0:
            mechanics_with_workload = mechanics_with_workload[:limit]
        
        response_data = {
            'mechanics': mechanics_with_workload,
            'total_mechanics': len(mechanics_with_workload),
            'sort_order': order,
            'message': f'Mechanics sorted by workload ({order}ending order)'
        }
        
        if limit:
            response_data['limit_applied'] = limit
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve mechanics by workload', 'message': str(e)}), 500


@mechanics_bp.route('/', methods=['GET'])
@cache.cached(timeout=600, key_prefix='all_mechanics')  # Cache for 10 minutes
def get_mechanics():
    """
    Get all mechanics.
    
    Cached: 10 minutes (600 seconds)
    WHY: Mechanics list is frequently accessed but changes infrequently.
    Caching reduces database load and improves response times for this
    common read operation. Cache is invalidated when mechanics are added/updated/deleted.
    """
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
        
        # Clear the cached mechanics list since we updated a mechanic
        cache.delete('all_mechanics')
        
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
        
        # Clear the cached mechanics list since we deleted a mechanic
        cache.delete('all_mechanics')
        
        return jsonify({'message': 'Mechanic deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500