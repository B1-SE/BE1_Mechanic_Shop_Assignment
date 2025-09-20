"""
Database models for the mechanic shop application.
"""

from app.extensions import db

# Association table for the Many-to-Many relationship between ServiceTicket and Mechanic
service_mechanics = db.Table('service_mechanics',
    db.Column('ticket_id', db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True),
    db.Column('mechanic_id', db.Integer, db.ForeignKey('mechanics.id'), primary_key=True)
)

# Association table for the Many-to-Many relationship between ServiceTicket and Inventory
service_inventory = db.Table('service_inventory',
    db.Column('ticket_id', db.Integer, db.ForeignKey('service_tickets.id'), primary_key=True),
    db.Column('inventory_id', db.Integer, db.ForeignKey('inventory.id'), primary_key=True)
)

# Import all models
from .customer import Customer
from .mechanic import Mechanic
from .service_ticket import ServiceTicket
from .inventory import Inventory

# Make models available for import
__all__ = ['Customer', 'Mechanic', 'ServiceTicket', 'Inventory', 'service_mechanics', 'service_inventory']