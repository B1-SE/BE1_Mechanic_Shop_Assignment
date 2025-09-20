"""
Customer schema for validation and serialization.
"""

from marshmallow import fields, validate, post_load
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.customer import Customer


class CustomerSchema(SQLAlchemyAutoSchema):
    """Schema for Customer model validation and serialization."""
    
    first_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    last_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    email = fields.Email(required=True)
    phone_number = fields.Str(validate=validate.Length(max=20))
    password = fields.Str(required=True, validate=validate.Length(min=6), load_only=True)
    
    class Meta:
        model = Customer
        include_fk = True
        load_instance = False
        exclude = ['password_hash']  # Never expose password hash in API responses
    
    @post_load
    def hash_password(self, data, **kwargs):
        """Hash the password before creating/updating the customer."""
        if 'password' in data:
            # Create a Customer instance to use the set_password method
            customer = Customer()
            customer.set_password(data['password'])
            data['password_hash'] = customer.password_hash
            del data['password']  # Remove plain password
        return data


class LoginSchema(SQLAlchemyAutoSchema):
    """Schema for customer login - only email and password."""
    
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=1))
    
    class Meta:
        model = Customer
        fields = ('email', 'password')
        load_instance = False


# Initialize schema instances
customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = LoginSchema()