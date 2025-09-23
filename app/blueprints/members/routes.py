"""
Member routes for the mechanic shop API.
"""

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.extensions import db, cache, limiter
from app.models.member import Member
from .schemas import (
    member_create_schema,
    member_update_schema,
    member_response_schema,
    members_response_schema,
)

# Create member blueprint
members_bp = Blueprint("members", __name__)


@members_bp.route("/", methods=["POST"])
@limiter.limit("5 per minute")  # Rate limit member creation
def create_member():
    """
    Create a new member.

    Rate Limited: 5 requests per minute per IP address
    WHY: Prevents spam member account creation and protects against
    automated attacks that could flood the system with fake accounts.
    """
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"message": "No input data provided"}), 400

        # Validate and load the data
        member_data = member_create_schema.load(json_data)

        # Check if email already exists
        existing_member = Member.query.filter_by(email=member_data["email"]).first()
        if existing_member:
            return (
                jsonify({"error": "Email already associated with another member"}),
                400,
            )

        # Create new member
        new_member = Member(
            first_name=member_data["first_name"],
            last_name=member_data["last_name"],
            email=member_data["email"],
            phone_number=member_data.get("phone_number"),
            role=member_data.get("role", "member"),
            is_active=member_data.get("is_active", True),
        )

        # Set password hash
        new_member.set_password(member_data["password"])

        db.session.add(new_member)
        db.session.commit()

        # Clear the cached members list since we added a new member
        cache.delete("all_members")

        return (
            jsonify(
                {
                    "message": "Member created successfully",
                    "member": member_response_schema.dump(new_member),
                }
            ),
            201,
        )

    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create member", "message": str(e)}), 500


@members_bp.route("/", methods=["GET"])
@cache.cached(timeout=300, key_prefix="all_members")  # Cache for 5 minutes
def get_members():
    """
    Get all members.

    Query Parameters:
    - role: Filter by role (member, admin, manager)
    - is_active: Filter by active status (true, false)

    Cached: 5 minutes (300 seconds)
    WHY: Members list is frequently accessed but changes less often than other data.
    Caching reduces database load and improves response times for this
    common read operation. Cache is invalidated when members are added/updated/deleted.
    """
    try:
        # Get query parameters
        role_filter = request.args.get("role")
        is_active_filter = request.args.get("is_active")

        # Start with base query
        query = Member.query

        # Apply filters
        if role_filter:
            if role_filter not in ["member", "admin", "manager"]:
                return (
                    jsonify(
                        {
                            "error": "Invalid role",
                            "message": "role must be one of: member, admin, manager",
                        }
                    ),
                    400,
                )
            query = query.filter(Member.role == role_filter)

        if is_active_filter is not None:
            if is_active_filter.lower() == "true":
                query = query.filter(Member.is_active)
            elif is_active_filter.lower() == "false":
                query = query.filter(~Member.is_active)
            else:
                return (
                    jsonify(
                        {
                            "error": "Invalid is_active value",
                            "message": 'is_active must be "true" or "false"',
                        }
                    ),
                    400,
                )

        # Execute query
        members = query.all()

        response_data = {
            "members": members_response_schema.dump(members),
            "total_count": len(members),
        }

        # Add filter information to response
        if role_filter:
            response_data["filtered_by_role"] = role_filter
        if is_active_filter is not None:
            response_data["filtered_by_active_status"] = (
                is_active_filter.lower() == "true"
            )

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": "Failed to retrieve members", "message": str(e)}), 500


@members_bp.route("/<int:member_id>", methods=["GET"])
def get_member(member_id):
    """Get a single member by ID."""
    try:
        member = db.session.get(Member, member_id)

        if not member:
            return jsonify({"error": "Member not found"}), 404

        return jsonify({"member": member_response_schema.dump(member)}), 200

    except Exception as e:
        return jsonify({"error": "Failed to retrieve member", "message": str(e)}), 500


@members_bp.route("/<int:member_id>", methods=["PUT"])
def update_member(member_id):
    """Update a member by ID."""
    try:
        member = db.session.get(Member, member_id)

        if not member:
            return jsonify({"error": "Member not found"}), 404

        json_data = request.get_json()
        if not json_data:
            return jsonify({"error": "No input data provided"}), 400

        # Validate and load the data
        member_data = member_update_schema.load(json_data)

        # Check if email is being changed and already exists
        if "email" in member_data and member_data["email"] != member.email:
            existing_member = Member.query.filter_by(email=member_data["email"]).first()
            if existing_member:
                return (
                    jsonify({"error": "Email already associated with another member"}),
                    400,
                )

        # Update member attributes
        for key, value in member_data.items():
            if key == "password":
                member.set_password(value)
            else:
                setattr(member, key, value)

        db.session.commit()

        # Clear the cached members list since we updated a member
        cache.delete("all_members")

        return (
            jsonify(
                {
                    "message": "Member updated successfully",
                    "member": member_response_schema.dump(member),
                }
            ),
            200,
        )

    except ValidationError as err:
        return jsonify({"error": "Validation failed", "details": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update member", "message": str(e)}), 500


@members_bp.route("/<int:member_id>", methods=["DELETE"])
def delete_member(member_id):
    """Delete a member by ID."""
    try:
        member = db.session.get(Member, member_id)

        if not member:
            return jsonify({"error": "Member not found"}), 404

        # Store member info for response
        member_info = {
            "id": member.id,
            "name": f"{member.first_name} {member.last_name}",
            "email": member.email,
        }

        db.session.delete(member)
        db.session.commit()

        # Clear the cached members list since we deleted a member
        cache.delete("all_members")

        return (
            jsonify(
                {
                    "message": "Member deleted successfully",
                    "deleted_member": member_info,
                }
            ),
            200,
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete member", "message": str(e)}), 500


@members_bp.route("/roles", methods=["GET"])
def get_member_roles():
    """Get available member roles."""
    return (
        jsonify(
            {
                "roles": ["member", "admin", "manager"],
                "descriptions": {
                    "member": "Standard member with basic access",
                    "admin": "Administrator with full system access",
                    "manager": "Manager with elevated permissions",
                },
            }
        ),
        200,
    )


@members_bp.route("/by-role/<role>", methods=["GET"])
def get_members_by_role(role):
    """Get all members with a specific role."""
    try:
        if role not in ["member", "admin", "manager"]:
            return (
                jsonify(
                    {
                        "error": "Invalid role",
                        "message": "role must be one of: member, admin, manager",
                    }
                ),
                400,
            )

        members = Member.query.filter_by(role=role).all()

        return (
            jsonify(
                {
                    "role": role,
                    "members": members_response_schema.dump(members),
                    "count": len(members),
                }
            ),
            200,
        )

    except Exception as e:
        return (
            jsonify({"error": "Failed to retrieve members by role", "message": str(e)}),
            500,
        )
