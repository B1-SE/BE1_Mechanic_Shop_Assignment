"""
Inventory routes for the mechanic shop application.
"""

from flask import Blueprint, request, jsonify
from app.extensions import db, limiter
from app.models.inventory import InventoryItem
from decimal import Decimal, InvalidOperation

# Create inventory blueprint
inventory_bp = Blueprint('inventory', __name__)


@inventory_bp.route('/', methods=['GET'])
@limiter.limit("100 per minute")
def get_all_inventory():
    """Get all inventory items"""
    try:
        items = InventoryItem.query.all()
        result = []
        for item in items:
            result.append(item.to_dict())
        
        return jsonify({
            'inventory': result,
            'count': len(result)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inventory_bp.route('/<int:item_id>', methods=['GET'])
@limiter.limit("100 per minute")
def get_inventory_item(item_id):
    """Get a specific inventory item"""
    try:
        item = db.session.get(InventoryItem, item_id)
        if not item:
            return jsonify({'error': 'Inventory item not found'}), 404
        return jsonify(item.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@inventory_bp.route('/', methods=['POST'])
@limiter.limit("50 per minute")
def create_inventory_item():
    """Create a new inventory item"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'quantity', 'price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate numeric fields
        try:
            quantity = int(data['quantity'])
            if quantity < 0:
                return jsonify({'error': 'Quantity must be non-negative'}), 400
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid quantity format'}), 400
        
        try:
            price = Decimal(str(data['price']))
            if price < 0:
                return jsonify({'error': 'Price must be non-negative'}), 400
        except (InvalidOperation, ValueError, TypeError):
            return jsonify({'error': 'Invalid price format'}), 400
        
        # Create new inventory item
        item = InventoryItem(
            name=data['name'],
            description=data.get('description'),
            quantity=quantity,
            price=price,
            supplier=data.get('supplier'),
            category=data.get('category'),
            reorder_level=data.get('reorder_level', 0)
        )
        
        # Save to database
        db.session.add(item)
        db.session.commit()
        
        return jsonify(item.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@inventory_bp.route('/<int:item_id>', methods=['PUT'])
@limiter.limit("50 per minute")
def update_inventory_item(item_id):
    """Update an inventory item"""
    try:
        item = db.session.get(InventoryItem, item_id)
        if not item:
            return jsonify({'error': 'Inventory item not found'}), 404
            
        data = request.get_json()
        
        # Update fields with validation
        if 'name' in data:
            item.name = data['name']
        if 'description' in data:
            item.description = data['description']
        if 'quantity' in data:
            try:
                quantity = int(data['quantity'])
                if quantity < 0:
                    return jsonify({'error': 'Quantity must be non-negative'}), 400
                item.quantity = quantity
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid quantity format'}), 400
        if 'price' in data:
            try:
                price = Decimal(str(data['price']))
                if price < 0:
                    return jsonify({'error': 'Price must be non-negative'}), 400
                item.price = price
            except (InvalidOperation, ValueError, TypeError):
                return jsonify({'error': 'Invalid price format'}), 400
        if 'supplier' in data:
            item.supplier = data['supplier']
        if 'category' in data:
            item.category = data['category']
        if 'reorder_level' in data:
            item.reorder_level = data['reorder_level']
        
        db.session.commit()
        return jsonify(item.to_dict()), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@inventory_bp.route('/<int:item_id>', methods=['DELETE'])
@limiter.limit("50 per minute")
def delete_inventory_item(item_id):
    """Delete an inventory item"""
    try:
        item = db.session.get(InventoryItem, item_id)
        if not item:
            return jsonify({'error': 'Inventory item not found'}), 404
            
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'message': 'Inventory item deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500