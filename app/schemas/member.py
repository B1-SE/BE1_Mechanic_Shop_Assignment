"""
Member schemas for the mechanic shop application.
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validate
from app.models.member import Member
from app.extensions import db


class MemberSchema(SQLAlchemyAutoSchema):
    """Member schema for serialization/deserialization"""
    
    class Meta:
        model = Member
        sqla_session = db.session
        load_instance = True
    
    # Add validation
    customer_id = fields.Int(required=True)
    membership_type = fields.Str(validate=validate.OneOf(['basic', 'premium', 'vip']))
    points = fields.Int(validate=validate.Range(min=0))


# Schema instances
member_schema = MemberSchema()
members_schema = MemberSchema(many=True)