"""
Customer schema for validation and serialization.
"""

from marshmallow import fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.customer import Customer


class CustomerSchema(SQLAlchemyAutoSchema):
    """Schema for Customer model validation and serialization."""
    
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    phone_number = fields.Str(validate=validate.Length(max=20))
    
    class Meta:
        model = Customer
        include_fk = True
        load_instance = False


# Initialize schema instances
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)