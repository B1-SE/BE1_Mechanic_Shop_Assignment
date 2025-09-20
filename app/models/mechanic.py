"""
Mechanic model for the mechanic shop application.
"""

from app.extensions import db
from . import service_mechanics


class Mechanic(db.Model):
    """Mechanic model representing employees who perform vehicle services."""
    
    __tablename__ = 'mechanics'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    salary = db.Column(db.Float)
    
    # Relationships
    service_tickets = db.relationship('ServiceTicket', 
                                    secondary=service_mechanics, 
                                    back_populates='mechanics')

    def __repr__(self):
        return f"<Mechanic {self.name}>"
    
    def to_dict(self):
        """Convert mechanic to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'salary': self.salary
        }