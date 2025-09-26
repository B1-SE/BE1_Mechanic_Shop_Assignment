"""
Inventory routes for the mechanic shop API.
"""

from flask import jsonify, request
from marshmallow import ValidationError
from app.extensions import db, cache, limiter
from app.models.inventory import Inventory
from app.auth import mechanic_token_required
from .schemas import inventory_schema, inventories_schema
from . import inventory_bp


@inventory_bp.route("/", methods=["POST"])
@mechanic_token_required
def create_inventory_item(mechanic_id):
    """Create a new inventory item. Requires mechanic authentication."""
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"message": "No input data provided"}), 400

        inventory_data = inventory_schema.load(json_data)

        # Check if item with the same name already exists
        if Inventory.query.filter(Inventory.name.ilike(inventory_data["name"])).first():
            return jsonify({"error": "Inventory item with this name already exists"}), 409

        new_item = Inventory(**inventory_data)
        db.session.add(new_item)
        db.session.commit()

        cache.delete("all_inventory")  # Invalidate cache
        return jsonify(inventory_schema.dump(new_item)), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@inventory_bp.route("/bulk", methods=["POST"])
@mechanic_token_required
def bulk_create_inventory_items(mechanic_id):
    """Create multiple inventory items at once. Requires mechanic authentication."""
    try:
        json_data = request.get_json()
        if not isinstance(json_data, list):
            return jsonify({"error": "Input must be a list of inventory items"}), 400

        # Use many=True for bulk loading and validation
        inventory_data_list = inventories_schema.load(json_data)

        new_items = []
        for item_data in inventory_data_list:
            # Check for existing item name (case-insensitive)
            if Inventory.query.filter(Inventory.name.ilike(item_data["name"])).first():
                return (
                    jsonify(
                        {
                            "error": f"Inventory item with name '{item_data['name']}' already exists"
                        }
                    ),
                    409,
                )
            new_items.append(Inventory(**item_data))

        db.session.add_all(new_items)
        db.session.commit()

        cache.delete("all_inventory")  # Invalidate cache
        return jsonify(inventories_schema.dump(new_items)), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@inventory_bp.route("/", methods=["GET"])
@cache.cached(timeout=600, key_prefix="all_inventory")
def get_inventory_items():
    """
    Get all inventory items with pagination, sorting, and filtering.
    This endpoint is cached for 10 minutes.

    Query Parameters:
    - page: Page number (default: 1).
    - per_page: Items per page (default: 10, max: 100).
    - sort_by: Field to sort by (id, name, price; default: id).
    - sort_order: Sort order (asc, desc; default: asc).
    - name: Filter by name (partial, case-insensitive match).
    - min_price: Minimum price filter.
    - max_price: Maximum price filter.
    """
    try:
        # --- Query Building ---
        query = Inventory.query

        # --- Filtering ---
        if name := request.args.get("name"):
            query = query.filter(Inventory.name.ilike(f"%{name}%"))
        if min_price := request.args.get("min_price", type=float):
            query = query.filter(Inventory.price >= min_price)
        if max_price := request.args.get("max_price", type=float):
            query = query.filter(Inventory.price <= max_price)

        # --- Sorting ---
        sort_by = request.args.get("sort_by", "id")
        sort_order = request.args.get("sort_order", "asc")
        sort_column = getattr(Inventory, sort_by, Inventory.id)

        if sort_order.lower() == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # --- Pagination ---
        page = request.args.get("page", 1, type=int)
        per_page = request.args.get("per_page", 10, type=int)
        per_page = min(per_page, 100)  # Cap per_page at 100

        paginated_items = query.paginate(page=page, per_page=per_page, error_out=False)
        items = paginated_items.items

        response = {
            "items": inventories_schema.dump(items),
            "pagination": {
                "page": paginated_items.page,
                "per_page": paginated_items.per_page,
                "total_pages": paginated_items.pages,
                "total_items": paginated_items.total,
                "next_page": paginated_items.next_num,
                "prev_page": paginated_items.prev_num,
            },
        }

        return jsonify(response), 200

    except Exception as e:
        return (
            jsonify({"error": "Failed to retrieve inventory items", "message": str(e)}),
            500,
        )


@inventory_bp.route("/<int:item_id>", methods=["GET"])
def get_inventory_item(item_id):
    """Get a single inventory item by ID."""
    item = db.session.get(Inventory, item_id)
    if not item:
        return jsonify({"error": "Inventory item not found"}), 404
    return jsonify(inventory_schema.dump(item)), 200


@inventory_bp.route("/<int:item_id>", methods=["PUT"])
@mechanic_token_required
def update_inventory_item(item_id, **kwargs):
    """Update an inventory item. Requires mechanic authentication."""
    item = db.session.get(Inventory, item_id)
    if not item:
        return jsonify({"error": "Inventory item not found"}), 404

    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({"message": "No input data provided"}), 400

        inventory_data = inventory_schema.load(json_data, partial=True)

        # Check for name conflict if name is being changed
        if "name" in inventory_data and inventory_data["name"] != item.name:
            if Inventory.query.filter(
                Inventory.name.ilike(inventory_data["name"])
            ).first():
                return jsonify({"error": "Inventory item with this name already exists"}), 409

        for key, value in inventory_data.items():
            setattr(item, key, value)

        db.session.commit()
        cache.delete("all_inventory")  # Invalidate cache
        return jsonify(inventory_schema.dump(item)), 200

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500


@inventory_bp.route("/<int:item_id>", methods=["DELETE"])
@mechanic_token_required
def delete_inventory_item(item_id, **kwargs):
    """Delete an inventory item. Requires mechanic authentication."""
    item = db.session.get(Inventory, item_id)
    if not item:
        return jsonify({"error": "Inventory item not found"}), 404

    try:
        db.session.delete(item)
        db.session.commit()
        cache.delete("all_inventory")  # Invalidate cache
        return jsonify({"message": "Inventory item deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500