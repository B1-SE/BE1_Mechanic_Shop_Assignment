"""
Service Ticket schema for validation and serialization.
"""

from marshmallow import fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.service_ticket import ServiceTicket


class ServiceTicketSchema(SQLAlchemyAutoSchema):
    """Schema for ServiceTicket model validation and serialization."""
    
    class Meta:
        model = ServiceTicket
        include_fk = True
        load_instance = False
        
    id = fields.Integer(dump_only=True)
    customer_id = fields.Integer(required=True)
    description = fields.String(required=True, validate=validate.Length(min=1, max=500))
    service_date = fields.DateTime(required=True)
    mechanic_ids = fields.List(fields.Integer(), load_default=[])  # For loading mechanic assignments
    mechanics = fields.Nested('MechanicSchema', many=True, dump_only=True)  # For dumping assigned mechanics
    customer = fields.Nested('CustomerSchema', dump_only=True)  # For dumping customer details


# Schema instances for single and multiple service tickets
service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)