"""
Mechanic schema for validation and serialization.
"""

from marshmallow import fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.mechanic import Mechanic


class MechanicSchema(SQLAlchemyAutoSchema):
    """Schema for Mechanic model validation and serialization."""
    
    class Meta:
        model = Mechanic
        include_fk = True
        load_instance = False
        
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    phone = fields.String(validate=validate.Length(max=20))
    salary = fields.Float(validate=validate.Range(min=0))


# Schema instances for single and multiple mechanics
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)