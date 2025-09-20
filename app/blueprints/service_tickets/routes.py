"""
Service Ticket routes for the mechanic shop API.
"""

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from datetime import datetime
from app.extensions import db
from app.models.service_ticket import ServiceTicket
from app.models.mechanic import Mechanic
from app.models.customer import Customer
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


@service_tickets_bp.route('/<int:ticket_id>/assign-mechanic/<int:mechanic_id>', methods=['PUT'])
def assign_mechanic_to_ticket(ticket_id, mechanic_id):
    """Assign a mechanic to a service ticket."""
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