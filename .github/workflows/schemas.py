"""
Marshmallow schemas for mechanic resources.
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.mechanic import Mechanic


class MechanicSchema(SQLAlchemyAutoSchema):
    """Schema for serializing and deserializing Mechanic objects."""

    class Meta:
        model = Mechanic
        load_instance = True


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
