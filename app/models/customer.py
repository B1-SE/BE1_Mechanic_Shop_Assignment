"""
Customer model for the mechanic shop application.
"""

from app.extensions import db


class Customer(db.Model):
    """Customer model representing customers who bring vehicles for service."""
    
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(20))
    
    # Relationships
    service_tickets = db.relationship('ServiceTicket', backref='customer', lazy=True)

    def __repr__(self):
        return f"<Customer {self.first_name} {self.last_name}>"
    
    def to_dict(self):
        """Convert customer to dictionary representation."""
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone_number': self.phone_number
        }