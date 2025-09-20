"""
Service Ticket model for the mechanic shop application.
"""

from app.extensions import db
from . import service_mechanics, service_inventory


class ServiceTicket(db.Model):
    """Service ticket model representing work orders for vehicle maintenance."""
    
    __tablename__ = 'service_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(500), nullable=False)
    service_date = db.Column(db.DateTime, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    
    # Relationships
    mechanics = db.relationship('Mechanic', 
                              secondary=service_mechanics, 
                              back_populates='service_tickets')
    
    inventory_parts = db.relationship('Inventory', 
                                    secondary=service_inventory, 
                                    back_populates='service_tickets')

    def __repr__(self):
        return f"<ServiceTicket {self.id}: {self.description[:50]}>"
    
    def to_dict(self):
        """Convert service ticket to dictionary representation."""
        return {
            'id': self.id,
            'description': self.description,
            'service_date': self.service_date.isoformat() if self.service_date else None,
            'customer_id': self.customer_id
        }