"""
Mechanic schemas for the mechanic shop application.
"""

from marshmallow import fields, validate, Schema


class MechanicSchema(Schema):
    """Mechanic schema for serialization/deserialization"""

    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    phone = fields.Str(validate=validate.Length(max=20))
    salary = fields.Decimal(as_string=True, places=2, required=True)
    hire_date = fields.DateTime(dump_only=True)
    is_active = fields.Bool()
    specializations = fields.Str()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


# Schema instances
mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
