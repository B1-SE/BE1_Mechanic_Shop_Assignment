"""
Database models for the mechanic shop application.
"""

from app.extensions import db

# Association table for the Many-to-Many relationship between ServiceTicket and Mechanic
service_mechanics = db.Table('service_mechanics',
    db.Column('ticket_id', db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanics.id'), primary_key=True)
)

# Import all models
from .customer import Customer
from .mechanic import Mechanic
from .service_ticket import ServiceTicket

# Make models available for import
__all__ = ['Customer', 'Mechanic', 'ServiceTicket', 'service_mechanics']