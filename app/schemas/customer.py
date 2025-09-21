"""
Customer schemas for the mechanic shop application.
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validate, ValidationError
from app.models.customer import Customer
from app.extensions import db


class CustomerSchema(SQLAlchemyAutoSchema):
    """Customer schema for serialization/deserialization"""
    
    class Meta:
        model = Customer
        sqla_session = db.session
        load_instance = True
        exclude = ('password_hash',)
    
    # Add validation
    email = fields.Email(required=True)
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    phone_number = fields.Str(validate=validate.Length(max=20))
    password = fields.Str(load_only=True, validate=validate.Length(min=6))


# Schema instances
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)