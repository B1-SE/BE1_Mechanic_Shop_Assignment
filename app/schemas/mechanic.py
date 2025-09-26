"""
Mechanic schemas for the mechanic shop application.
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.mechanic import Mechanic


class MechanicSchema(SQLAlchemyAutoSchema):
    """Mechanic schema for serialization/deserialization"""

    class Meta:
        model = Mechanic
        load_instance = True
        include_fk = True


# Schema instances
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
