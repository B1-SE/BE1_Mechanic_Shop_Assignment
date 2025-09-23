"""
Service ticket schemas for the mechanic shop application.
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, validate
from app.models.service_ticket import ServiceTicket
from app.extensions import db


class ServiceTicketSchema(SQLAlchemyAutoSchema):
    """Service ticket schema for serialization/deserialization"""

    class Meta:
        model = ServiceTicket
        sqla_session = db.session
        load_instance = True

    # Add validation
    customer_id = fields.Int(required=True)
    vehicle_info = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(required=True, validate=validate.Length(min=1))
    status = fields.Str(
        validate=validate.OneOf(["pending", "in_progress", "completed", "cancelled"])
    )
    priority = fields.Str(validate=validate.OneOf(["low", "medium", "high", "urgent"]))
    estimated_cost = fields.Decimal(as_string=True, places=2)
    actual_cost = fields.Decimal(as_string=True, places=2)


# Schema instances
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
