# app/blueprints/inventory/routes.py
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Inventory
from app.extensions import db, cache
from app.utils.auth import token_required
from . import inventory_bp
from .schemas import InventorySchema

inventory_schema = InventorySchema()
inventory_list_schema = InventorySchema(many=True)

@inventory_bp.route('/', methods=['GET'])
@cache.cached(timeout=600, key_prefix='all_inventory')  # Cache for 10 minutes
def get_all_inventory():
    """Get all inventory items with optional pagination, sorting, and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Advanced query features
    query = Inventory.query
    
    # Filtering by name
    name_filter = request.args.get('name')
    if name_filter:
        query = query.filter(Inventory.name.ilike(f'%{name_filter}%'))
    
    # Filtering by price range
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    if min_price is not None:
        query = query.filter(Inventory.price >= min_price)
    if max_price is not None:
        query = query.filter(Inventory.price <= max_price)
    
    # Sorting
    sort_by = request.args.get('sort_by', 'id')
    sort_order = request.args.get('sort_order', 'asc')
    
    if hasattr(Inventory, sort_by):
        if sort_order.lower() == 'desc':
            query = query.order_by(getattr(Inventory, sort_by).desc())
        else:
            query = query.order_by(getattr(Inventory, sort_by))
    
    # Pagination
    if per_page > 100:  # Limit max per_page
        per_page = 100
    
    inventory_paginated = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'inventory': inventory_list_schema.dump(inventory_paginated.items),
        'pagination': {
            'total': inventory_paginated.total,
            'pages': inventory_paginated.pages,
            'current_page': inventory_paginated.page,
            'per_page': inventory_paginated.per_page,
            'has_next': inventory_paginated.has_next,
            'has_prev': inventory_paginated.has_prev
        }
    })

@inventory_bp.route('/<int:id>', methods=['GET'])
def get_inventory_by_id(id):
    """Get a specific inventory item by ID"""
    inventory_item = Inventory.query.get_or_404(id)
    return jsonify(inventory_schema.dump(inventory_item))

@inventory_bp.route('/', methods=['POST'])
@token_required
def create_inventory(current_user):
    """Create a new inventory item"""
    try:
        inventory_data = inventory_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # Check if inventory item with same name already exists
    existing_item = Inventory.query.filter_by(name=inventory_data['name']).first()
    if existing_item:
        return jsonify({'error': 'Inventory item with this name already exists'}), 409
    
    new_inventory = Inventory(
        name=inventory_data['name'],
        price=inventory_data['price']
    )
    
    db.session.add(new_inventory)
    db.session.commit()
    
    # Clear cache after creating new inventory
    cache.delete('all_inventory')
    
    return jsonify(inventory_schema.dump(new_inventory)), 201

@inventory_bp.route('/<int:id>', methods=['PUT'])
@token_required
def update_inventory(current_user, id):
    """Update an existing inventory item"""
    inventory_item = Inventory.query.get_or_404(id)
    
    try:
        inventory_data = inventory_schema.load(request.json, partial=True)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    # Check if updating name would create duplicate
    if 'name' in inventory_data and inventory_data['name'] != inventory_item.name:
        existing_item = Inventory.query.filter_by(name=inventory_data['name']).first()
        if existing_item:
            return jsonify({'error': 'Inventory item with this name already exists'}), 409
    
    # Update fields
    if 'name' in inventory_data:
        inventory_item.name = inventory_data['name']
    if 'price' in inventory_data:
        inventory_item.price = inventory_data['price']
    
    db.session.commit()
    
    # Clear cache after updating inventory
    cache.delete('all_inventory')
    
    return jsonify(inventory_schema.dump(inventory_item))

@inventory_bp.route('/<int:id>', methods=['DELETE'])
@token_required
def delete_inventory(current_user, id):
    """Delete an inventory item"""
    inventory_item = Inventory.query.get_or_404(id)
    
    db.session.delete(inventory_item)
    db.session.commit()
    
    # Clear cache after deleting inventory
    cache.delete('all_inventory')
    
    return jsonify({'message': 'Inventory item deleted successfully'}), 200

@inventory_bp.route('/bulk', methods=['POST'])
@token_required
def create_bulk_inventory(current_user):
    """Create multiple inventory items at once"""
    try:
        inventory_list = inventory_list_schema.load(request.json)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 400
    
    created_items = []
    errors = []
    
    for item_data in inventory_list:
        # Check for duplicates
        existing_item = Inventory.query.filter_by(name=item_data['name']).first()
        if existing_item:
            errors.append(f'Inventory item "{item_data["name"]}" already exists')
            continue
        
        new_inventory = Inventory(
            name=item_data['name'],
            price=item_data['price']
        )
        
        db.session.add(new_inventory)
        created_items.append(new_inventory)
    
    if created_items:
        db.session.commit()
        # Clear cache after bulk creation
        cache.delete('all_inventory')
    
    response = {
        'created': inventory_list_schema.dump(created_items),
        'created_count': len(created_items)
    }
    
    if errors:
        response['errors'] = errors
        response['error_count'] = len(errors)
    
    return jsonify(response), 201 if created_items else 400