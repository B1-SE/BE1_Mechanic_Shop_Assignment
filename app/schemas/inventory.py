"""
Inventory schemas for the mechanic shop application.
"""

from marshmallow import fields, validate, Schema


class InventoryItemSchema(Schema):
    """Inventory item schema for serialization/deserialization"""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str()
    quantity = fields.Int(required=True, validate=validate.Range(min=0))
    price = fields.Decimal(
        required=True, as_string=True, places=2, validate=validate.Range(min=0)
    )
    supplier = fields.Str(validate=validate.Length(max=100))
    category = fields.Str(validate=validate.Length(max=50))
    reorder_level = fields.Int(validate=validate.Range(min=0))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


# Schema instances
inventory_item_schema = InventoryItemSchema()
inventory_items_schema = InventoryItemSchema(many=True)
