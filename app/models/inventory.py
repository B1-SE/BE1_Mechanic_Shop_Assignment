"""
Inventory model for the mechanic shop application.
"""

from app.extensions import db


class Inventory(db.Model):
    """Inventory model representing parts and supplies in the shop."""
    
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    # Many-to-many relationship with ServiceTicket
    service_tickets = db.relationship('ServiceTicket', 
                                    secondary='service_inventory', 
                                    back_populates='inventory_parts')

    def __repr__(self):
        return f"<Inventory {self.id}: {self.name} - ${self.price}>"
    
    def to_dict(self):
        """Convert inventory item to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price
        }