"""
Service Ticket routes for the mechanic shop API.
"""

from flask import jsonify, request
from marshmallow import ValidationError
from app.extensions import db, limiter, cache
from app.models.service_ticket import ServiceTicket
from app.models.mechanic import Mechanic
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.auth import token_required, mechanic_token_required
from .schemas import service_ticket_schema, service_tickets_schema
from . import service_tickets_bp

@service_tickets_bp.route("/", methods=["POST"])
@token_required
def create_service_ticket(customer_id):
    """Create a new service ticket."""
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"message": "No input data provided"}), 400

        # Validate and load the data
        # Customer ID is from the token, so we exclude it from loading
        service_ticket_data = service_ticket_schema.load(
            json_data, partial=("mechanics", "customer_id")
        )

        # Create new service ticket
        new_service_ticket = ServiceTicket(
            customer_id=customer_id,  # Use customer_id from the token
            description=service_ticket_data.get("description"),
            service_date=service_ticket_data.get("service_date"),
        )

        # Assign mechanics if provided
        if (
            "mechanic_ids" in service_ticket_data
            and service_ticket_data["mechanic_ids"]
        ):
            for mechanic_id in set(service_ticket_data["mechanic_ids"]):
                mechanic = db.session.get(Mechanic, mechanic_id)
                if mechanic:
                    new_service_ticket.mechanics.append(mechanic)

        db.session.add(new_service_ticket)
        db.session.commit()

        return jsonify(service_ticket_schema.dump(new_service_ticket)), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 400


@service_tickets_bp.route("/", methods=["GET"])
@mechanic_token_required
def get_service_tickets(mechanic_id):
    """Get all service tickets."""
    service_tickets = ServiceTicket.query.all()
    return jsonify(service_tickets_schema.dump(service_tickets)), 200

@service_tickets_bp.route(
    "/<int:ticket_id>/assign-mechanic/<int:mechanic_id>", methods=["PUT"]
)
@limiter.limit("20 per minute")  # Rate limit mechanic assignments
@mechanic_token_required
def assign_mechanic_to_ticket(ticket_id, mechanic_id, **kwargs):
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
        return (
            jsonify({"message": "Mechanic already assigned to this service ticket"}),
            400,
        )

    try:
        service_ticket.mechanics.append(mechanic)
        db.session.commit()
        return (
            jsonify(
                {
                    "message": f"Mechanic {mechanic.name} assigned to service ticket {ticket_id}",
                    "service_ticket": service_ticket_schema.dump(service_ticket),
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@service_tickets_bp.route(
    "/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"]
)
@mechanic_token_required
def remove_mechanic_from_ticket(ticket_id, mechanic_id, **kwargs):
    """Remove a mechanic from a service ticket."""
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    # Check if mechanic is assigned to this ticket
    if mechanic not in service_ticket.mechanics:
        return (
            jsonify({"message": "Mechanic is not assigned to this service ticket"}),
            400,
        )

    try:
        service_ticket.mechanics.remove(mechanic)
        db.session.commit()
        return (
            jsonify(
                {
                    "message": f"Mechanic {mechanic.name} removed from service ticket {ticket_id}",
                    "service_ticket": service_ticket_schema.dump(service_ticket),
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@service_tickets_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
@mechanic_token_required
def edit_ticket_mechanics(ticket_id, **kwargs):
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

    json_data = request.get_json()
    if not json_data:
        return jsonify({"message": "No input data provided"}), 400

    add_ids = set(json_data.get("add_ids", []))
    remove_ids = set(json_data.get("remove_ids", []))

    if not add_ids and not remove_ids:
        return jsonify({"message": "No add_ids or remove_ids provided"}), 400

    try:
        # Fetch all relevant mechanics in one query for efficiency
        all_ids = add_ids.union(remove_ids)
        mechanics_to_process = Mechanic.query.filter(Mechanic.id.in_(all_ids)).all()
        mechanics_map = {m.id: m for m in mechanics_to_process}

        changes_made = []
        errors = []

        # Process removals
        for mech_id in remove_ids:
            mechanic = mechanics_map.get(mech_id)
            if not mechanic:
                errors.append(f"Mechanic with ID {mech_id} not found for removal.")
                continue
            if mechanic in service_ticket.mechanics:
                service_ticket.mechanics.remove(mechanic)
                changes_made.append(f"Removed mechanic {mechanic.name} (ID: {mech_id})")
            else:
                errors.append(f"Mechanic {mechanic.name} (ID: {mech_id}) was not assigned to this ticket.")

        # Process additions
        for mech_id in add_ids:
            mechanic = mechanics_map.get(mech_id)
            if not mechanic:
                errors.append(f"Mechanic with ID {mech_id} not found for addition.")
                continue
            if mechanic not in service_ticket.mechanics:
                service_ticket.mechanics.append(mechanic)
                changes_made.append(f"Added mechanic {mechanic.name} (ID: {mech_id})")
            else:
                errors.append(f"Mechanic {mechanic.name} (ID: {mech_id}) is already assigned to this ticket.")

        if changes_made:
            db.session.commit()

        response_data = {
            "message": "Mechanic assignments updated.",
            "changes_made": changes_made,
            "errors": errors,
            "service_ticket": service_ticket_schema.dump(service_ticket),
        }

        if not errors:
            return jsonify(response_data), 200
        elif changes_made:
            return jsonify(response_data), 207 # Multi-Status for partial success
        else:
            return jsonify(response_data), 400 # Bad Request if only errors occurred

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500


@service_tickets_bp.route(
    "/<int:ticket_id>/inventory/<int:inventory_id>", methods=["POST"]
)
@mechanic_token_required
def add_inventory_to_ticket(ticket_id, inventory_id, **kwargs):
    """Add a single inventory item to a service ticket."""
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    inventory_item = db.session.get(Inventory, inventory_id)
    if not inventory_item:
        return jsonify({"error": "Inventory item not found"}), 404

    # Check if inventory item is already added
    if inventory_item in service_ticket.inventory_parts:
        return (
            jsonify({"message": "Inventory item already added to this service ticket"}),
            400,
        )

    try:
        service_ticket.inventory_parts.append(inventory_item)
        db.session.commit()
        return (
            jsonify(
                {
                    "message": f"Inventory item '{inventory_item.name}' added to service ticket {ticket_id}",
                    "service_ticket": service_ticket_schema.dump(service_ticket),
                }
            ),
            200,
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@service_tickets_bp.route("/<int:ticket_id>/cost", methods=["GET"])
@mechanic_token_required
def get_service_ticket_cost(ticket_id, **kwargs):
    """Calculate the total cost of parts for a service ticket."""
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    try:
        # Calculate total cost from inventory parts
        total_parts_cost = sum(part.price for part in service_ticket.inventory_parts)

        # Prepare a detailed list of parts for the response
        parts_breakdown = [
            {"id": part.id, "name": part.name, "price": float(part.price)}
            for part in service_ticket.inventory_parts
        ]

        return jsonify({
            "ticket_id": ticket_id,
            "total_parts_cost": float(total_parts_cost),
            "parts_count": len(parts_breakdown),
            "parts_breakdown": parts_breakdown
        }), 200

    except Exception as e:
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500
