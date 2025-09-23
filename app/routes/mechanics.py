"""
Mechanic routes for the mechanic shop application.
"""

from flask import Blueprint, request, jsonify
from app.extensions import db, limiter
from app.models.mechanic import Mechanic
from app.schemas.mechanic import mechanic_schema, mechanics_schema
from marshmallow import ValidationError

mechanics_bp = Blueprint("mechanics", __name__)


@mechanics_bp.route("/", methods=["GET"])
@limiter.limit("100 per minute")
def get_all_mechanics():
    """Get all mechanics"""
    try:
        mechanics = Mechanic.query.all()
        result = mechanics_schema.dump(mechanics)
        return jsonify({"mechanics": result, "count": len(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mechanics_bp.route("/", methods=["POST"])
@limiter.limit("50 per minute")
def create_mechanic():
    """Create a new mechanic"""
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "No input data provided"}), 400

        # Validate and deserialize data using Marshmallow schema
        mechanic_data = mechanic_schema.load(json_data)

        # Check if mechanic already exists
        existing_mechanic = Mechanic.query.filter_by(
            email=mechanic_data["email"]
        ).first()
        if existing_mechanic:
            return jsonify({"error": "Mechanic with this email already exists"}), 400

        # Create new mechanic
        mechanic = Mechanic(**mechanic_data)

        db.session.add(mechanic)
        db.session.commit()

        return jsonify(mechanic_schema.dump(mechanic)), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@mechanics_bp.route("/<int:mechanic_id>", methods=["GET"])
@limiter.limit("100 per minute")
def get_mechanic(mechanic_id):
    """Get a specific mechanic"""
    try:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({"error": "Mechanic not found"}), 404

        return jsonify(mechanic_schema.dump(mechanic)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@mechanics_bp.route("/<int:mechanic_id>", methods=["PUT"])
@limiter.limit("50 per minute")
def update_mechanic(mechanic_id):
    """Update a mechanic"""
    try:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({"error": "Mechanic not found"}), 404

        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "No input data provided"}), 400

        # Validate and load data for partial update
        mechanic_data = mechanic_schema.load(json_data, partial=True)

        # Update fields from validated data
        for key, value in mechanic_data.items():
            setattr(mechanic, key, value)

        db.session.commit()
        return jsonify(mechanic_schema.dump(mechanic)), 200
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@mechanics_bp.route("/<int:mechanic_id>", methods=["DELETE"])
@limiter.limit("30 per minute")
def delete_mechanic(mechanic_id):
    """Delete a mechanic"""
    try:
        mechanic = db.session.get(Mechanic, mechanic_id)
        if not mechanic:
            return jsonify({"error": "Mechanic not found"}), 404

        db.session.delete(mechanic)
        db.session.commit()

        return jsonify({"message": "Mechanic deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
