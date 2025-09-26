"""
Mechanics blueprint schemas - imports from main schemas.
"""
from app.extensions import ma
from app.models.mechanic import Mechanic


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    """Schema for serializing and deserializing Mechanic objects."""

    class Meta:
        model = Mechanic
        load_instance = True
        include_fk = True


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
