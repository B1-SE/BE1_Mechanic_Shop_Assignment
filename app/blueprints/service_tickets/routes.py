"""
Service Ticket routes for the mechanic shop API.
"""

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from datetime import datetime
from app.extensions import db, limiter
from app.models.service_ticket import ServiceTicket
from app.models.mechanic import Mechanic
from app.models.customer import Customer
from app.models.inventory import Inventory
from .schemas import service_ticket_schema, service_tickets_schema

# Create service tickets blueprint
service_tickets_bp = Blueprint('service_tickets', __name__)


@service_tickets_bp.route('/', methods=['POST'])
def create_service_ticket():
    """Create a new service ticket."""
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400

        # Validate and load the data
        service_ticket_data = service_ticket_schema.load(json_data)
        
        # Check if customer exists
        customer = db.session.get(Customer, service_ticket_data['customer_id'])
        if not customer:
            return jsonify({"error": "Customer not found"}), 400
        
        # Create new service ticket
        new_service_ticket = ServiceTicket(
            customer_id=service_ticket_data['customer_id'],
            description=service_ticket_data['description'],
            service_date=service_ticket_data['service_date']
        )
        
        # Assign mechanics if provided
        if 'mechanic_ids' in service_ticket_data and service_ticket_data['mechanic_ids']:
            for mechanic_id in service_ticket_data['mechanic_ids']:
                mechanic = db.session.get(Mechanic, mechanic_id)
                if mechanic:
                    new_service_ticket.mechanics.append(mechanic)
        
        db.session.add(new_service_ticket)
        db.session.commit()

        return jsonify(service_ticket_schema.dump(new_service_ticket)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400


@service_tickets_bp.route('/', methods=['GET'])
def get_service_tickets():
    """Get all service tickets."""
    service_tickets = ServiceTicket.query.all()
    return jsonify(service_tickets_schema.dump(service_tickets)), 200


@service_tickets_bp.route('/<int:ticket_id>', methods=['GET'])
def get_service_ticket(ticket_id):
    """Get a single service ticket by ID."""
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    
    if service_ticket:
        return jsonify(service_ticket_schema.dump(service_ticket)), 200
    
    return jsonify({"error": "Service ticket not found"}), 404


@service_tickets_bp.route('/<int:ticket_id>', methods=['PUT'])
def update_service_ticket(ticket_id):
    """Update a service ticket by ID."""
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
            
        service_ticket_data = service_ticket_schema.load(json_data, partial=True)
        
        # Update basic fields
        if 'description' in service_ticket_data:
            service_ticket.description = service_ticket_data['description']
        if 'service_date' in service_ticket_data:
            service_ticket.service_date = service_ticket_data['service_date']
        if 'customer_id' in service_ticket_data:
            # Verify customer exists
            customer = db.session.get(Customer, service_ticket_data['customer_id'])
            if not customer:
                return jsonify({"error": "Customer not found"}), 400
            service_ticket.customer_id = service_ticket_data['customer_id']

        db.session.commit()
        return jsonify(service_ticket_schema.dump(service_ticket)), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400


@service_tickets_bp.route('/<int:ticket_id>', methods=['DELETE'])
def delete_service_ticket(ticket_id):
    """Delete a service ticket by ID."""
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    try:
        db.session.delete(service_ticket)
        db.session.commit()
        return jsonify({'message': 'Service ticket deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@service_tickets_bp.route('/<int:ticket_id>/edit', methods=['PUT'])
def edit_ticket_mechanics(ticket_id):
    """
    Bulk add and remove mechanics from a service ticket.
    
    Expects JSON with:
    - add_ids: List of mechanic IDs to add to the ticket
    - remove_ids: List of mechanic IDs to remove from the ticket
    
    Example:
    {
        "add_ids": [1, 2, 3],
        "remove_ids": [4, 5]
    }
    """
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
        
        add_ids = json_data.get('add_ids', [])
        remove_ids = json_data.get('remove_ids', [])
        
        # Validate that add_ids and remove_ids are lists
        if not isinstance(add_ids, list):
            return jsonify({'error': 'add_ids must be a list of mechanic IDs'}), 400
        if not isinstance(remove_ids, list):
            return jsonify({'error': 'remove_ids must be a list of mechanic IDs'}), 400
        
        changes_made = []
        errors = []
        
        # Process removals first
        for mechanic_id in remove_ids:
            mechanic = db.session.get(Mechanic, mechanic_id)
            if not mechanic:
                errors.append(f"Mechanic with ID {mechanic_id} not found")
                continue
            
            if mechanic in service_ticket.mechanics:
                service_ticket.mechanics.remove(mechanic)
                changes_made.append(f"Removed mechanic {mechanic.name} (ID: {mechanic_id})")
            else:
                errors.append(f"Mechanic {mechanic.name} (ID: {mechanic_id}) was not assigned to this ticket")
        
        # Process additions
        for mechanic_id in add_ids:
            mechanic = db.session.get(Mechanic, mechanic_id)
            if not mechanic:
                errors.append(f"Mechanic with ID {mechanic_id} not found")
                continue
            
            if mechanic not in service_ticket.mechanics:
                service_ticket.mechanics.append(mechanic)
                changes_made.append(f"Added mechanic {mechanic.name} (ID: {mechanic_id})")
            else:
                errors.append(f"Mechanic {mechanic.name} (ID: {mechanic_id}) was already assigned to this ticket")
        
        # Commit changes if any were made
        if changes_made:
            db.session.commit()
        
        # Prepare response
        response_data = {
            "message": f"Processed {len(add_ids + remove_ids)} mechanic changes for ticket {ticket_id}",
            "changes_made": changes_made,
            "service_ticket": service_ticket_schema.dump(service_ticket)
        }
        
        if errors:
            response_data["errors"] = errors
        
        # Return appropriate status code
        if changes_made and not errors:
            return jsonify(response_data), 200
        elif changes_made and errors:
            return jsonify(response_data), 207  # Multi-Status (partial success)
        elif not changes_made and errors:
            return jsonify(response_data), 400  # Bad Request (no changes made)
        else:
            return jsonify({
                "message": "No changes requested",
                "service_ticket": service_ticket_schema.dump(service_ticket)
            }), 200
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to edit ticket mechanics', 'message': str(e)}), 500


@service_tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
@limiter.limit("20 per minute")  # Rate limit mechanic assignments
def assign_mechanic_to_ticket(ticket_id, mechanic_id):
    """
    Assign a mechanic to a service ticket.
    
    Rate Limited: 20 requests per minute per IP address
    WHY: Prevents rapid-fire mechanic assignments that could overwhelm
    mechanics with too many tickets at once, and protects against
    automated abuse of the assignment system.
    """
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404
        
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    # Check if mechanic is already assigned
    if mechanic in service_ticket.mechanics:
        return jsonify({"message": "Mechanic already assigned to this service ticket"}), 400
    
    try:
        service_ticket.mechanics.append(mechanic)
        db.session.commit()
        return jsonify({
            "message": f"Mechanic {mechanic.name} assigned to service ticket {ticket_id}",
            "service_ticket": service_ticket_schema.dump(service_ticket)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@service_tickets_bp.route('/<int:ticket_id>/remove-mechanic/<int:mechanic_id>', methods=['PUT'])
def remove_mechanic_from_ticket(ticket_id, mechanic_id):
    """Remove a mechanic from a service ticket."""
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404
        
    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404
    
    # Check if mechanic is assigned to this ticket
    if mechanic not in service_ticket.mechanics:
        return jsonify({"message": "Mechanic is not assigned to this service ticket"}), 400
    
    try:
        service_ticket.mechanics.remove(mechanic)
        db.session.commit()
        return jsonify({
            "message": f"Mechanic {mechanic.name} removed from service ticket {ticket_id}",
            "service_ticket": service_ticket_schema.dump(service_ticket)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@service_tickets_bp.route('/<int:ticket_id>/inventory', methods=['POST'])
def add_inventory_to_ticket(ticket_id):
    """
    Add inventory parts to a service ticket.
    
    Expects JSON with:
    - inventory_ids: List of inventory item IDs to add to the ticket
    
    Example:
    {
        "inventory_ids": [1, 2, 3]
    }
    """
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
        
        inventory_ids = json_data.get('inventory_ids', [])
        
        # Validate that inventory_ids is a list
        if not isinstance(inventory_ids, list):
            return jsonify({'error': 'inventory_ids must be a list of inventory IDs'}), 400
        
        changes_made = []
        errors = []
        
        # Process additions
        for inventory_id in inventory_ids:
            inventory_item = db.session.get(Inventory, inventory_id)
            if not inventory_item:
                errors.append(f"Inventory item with ID {inventory_id} not found")
                continue
            
            if inventory_item not in service_ticket.inventory_parts:
                service_ticket.inventory_parts.append(inventory_item)
                changes_made.append(f"Added inventory item {inventory_item.name} (ID: {inventory_id})")
            else:
                errors.append(f"Inventory item {inventory_item.name} (ID: {inventory_id}) was already added to this ticket")
        
        # Commit changes if any were made
        if changes_made:
            db.session.commit()
        
        # Prepare response
        response_data = {
            "message": f"Processed {len(inventory_ids)} inventory additions for ticket {ticket_id}",
            "changes_made": changes_made,
            "service_ticket": service_ticket_schema.dump(service_ticket)
        }
        
        if errors:
            response_data["errors"] = errors
        
        # Return appropriate status code
        if changes_made and not errors:
            return jsonify(response_data), 200
        elif changes_made and errors:
            return jsonify(response_data), 207  # Multi-Status (partial success)
        elif not changes_made and errors:
            return jsonify(response_data), 400  # Bad Request (no changes made)
        else:
            return jsonify({
                "message": "No changes requested",
                "service_ticket": service_ticket_schema.dump(service_ticket)
            }), 200
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to add inventory to ticket', 'message': str(e)}), 500


@service_tickets_bp.route('/<int:ticket_id>/inventory', methods=['DELETE'])
def remove_inventory_from_ticket(ticket_id):
    """
    Remove inventory parts from a service ticket.
    
    Expects JSON with:
    - inventory_ids: List of inventory item IDs to remove from the ticket
    
    Example:
    {
        "inventory_ids": [1, 2, 3]
    }
    """
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404
    
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
        
        inventory_ids = json_data.get('inventory_ids', [])
        
        # Validate that inventory_ids is a list
        if not isinstance(inventory_ids, list):
            return jsonify({'error': 'inventory_ids must be a list of inventory IDs'}), 400
        
        changes_made = []
        errors = []
        
        # Process removals
        for inventory_id in inventory_ids:
            inventory_item = db.session.get(Inventory, inventory_id)
            if not inventory_item:
                errors.append(f"Inventory item with ID {inventory_id} not found")
                continue
            
            if inventory_item in service_ticket.inventory_parts:
                service_ticket.inventory_parts.remove(inventory_item)
                changes_made.append(f"Removed inventory item {inventory_item.name} (ID: {inventory_id})")
            else:
                errors.append(f"Inventory item {inventory_item.name} (ID: {inventory_id}) was not assigned to this ticket")
        
        # Commit changes if any were made
        if changes_made:
            db.session.commit()
        
        # Prepare response
        response_data = {
            "message": f"Processed {len(inventory_ids)} inventory removals for ticket {ticket_id}",
            "changes_made": changes_made,
            "service_ticket": service_ticket_schema.dump(service_ticket)
        }
        
        if errors:
            response_data["errors"] = errors
        
        # Return appropriate status code
        if changes_made and not errors:
            return jsonify(response_data), 200
        elif changes_made and errors:
            return jsonify(response_data), 207  # Multi-Status (partial success)
        elif not changes_made and errors:
            return jsonify(response_data), 400  # Bad Request (no changes made)
        else:
            return jsonify({
                "message": "No changes requested",
                "service_ticket": service_ticket_schema.dump(service_ticket)
            }), 200
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to remove inventory from ticket', 'message': str(e)}), 500


@service_tickets_bp.route('/<int:ticket_id>/inventory/<int:inventory_id>', methods=['POST'])
def add_single_inventory_to_ticket(ticket_id, inventory_id):
    """Add a single inventory item to a service ticket."""
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404
        
    inventory_item = db.session.get(Inventory, inventory_id)
    if not inventory_item:
        return jsonify({"error": "Inventory item not found"}), 404
    
    # Check if inventory item is already added
    if inventory_item in service_ticket.inventory_parts:
        return jsonify({"message": "Inventory item already added to this service ticket"}), 400
    
    try:
        service_ticket.inventory_parts.append(inventory_item)
        db.session.commit()
        return jsonify({
            "message": f"Inventory item {inventory_item.name} added to service ticket {ticket_id}",
            "service_ticket": service_ticket_schema.dump(service_ticket)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500


@service_tickets_bp.route('/<int:ticket_id>/inventory/<int:inventory_id>', methods=['DELETE'])
def remove_single_inventory_from_ticket(ticket_id, inventory_id):
    """Remove a single inventory item from a service ticket."""
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404
        
    inventory_item = db.session.get(Inventory, inventory_id)
    if not inventory_item:
        return jsonify({"error": "Inventory item not found"}), 404
    
    # Check if inventory item is assigned to this ticket
    if inventory_item not in service_ticket.inventory_parts:
        return jsonify({"message": "Inventory item is not assigned to this service ticket"}), 400
    
    try:
        service_ticket.inventory_parts.remove(inventory_item)
        db.session.commit()
        return jsonify({
            "message": f"Inventory item {inventory_item.name} removed from service ticket {ticket_id}",
            "service_ticket": service_ticket_schema.dump(service_ticket)
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500