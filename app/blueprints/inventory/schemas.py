"""
Inventory blueprint schemas.
"""
from app.extensions import ma
from app.models.inventory import Inventory


class InventorySchema(ma.SQLAlchemyAutoSchema):
    """Schema for serializing and deserializing Inventory objects."""

    class Meta:
        model = Inventory
        load_instance = True
        include_fk = True


inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)