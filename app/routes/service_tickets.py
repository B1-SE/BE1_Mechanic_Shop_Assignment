"""
Service ticket routes for the mechanic shop application.
"""

from flask import Blueprint, request, jsonify
from app.extensions import db, limiter
from app.models.service_ticket import ServiceTicket

# Create service tickets blueprint
service_tickets_bp = Blueprint("service_tickets", __name__)


@service_tickets_bp.route("/", methods=["GET"])
@limiter.limit("100 per minute")
def get_all_service_tickets():
    """Get all service tickets"""
    try:
        service_tickets = ServiceTicket.query.all()
        result = []
        for ticket in service_tickets:
            result.append(ticket.to_dict())

        return jsonify({"service_tickets": result, "count": len(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@service_tickets_bp.route("/<int:ticket_id>", methods=["GET"])
@limiter.limit("100 per minute")
def get_service_ticket(ticket_id):
    """Get a specific service ticket"""
    try:
        ticket = db.session.get(ServiceTicket, ticket_id)
        if not ticket:
            return jsonify({"error": "Service ticket not found"}), 404
        return jsonify(ticket.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@service_tickets_bp.route("/", methods=["POST"])
@limiter.limit("50 per minute")
def create_service_ticket():
    """Create a new service ticket"""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ["customer_id", "vehicle_info", "description"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Create new service ticket
        ticket = ServiceTicket(
            customer_id=data["customer_id"],
            vehicle_info=data["vehicle_info"],
            description=data["description"],
            estimated_cost=data.get("estimated_cost", 0.0),
            status=data.get("status", "pending"),
        )

        # Save to database
        db.session.add(ticket)
        db.session.commit()

        return jsonify(ticket.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
