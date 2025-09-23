"""
Service ticket model for the mechanic shop application.
"""

from app.extensions import db
from datetime import datetime, timezone


class ServiceTicket(db.Model):
    """Service ticket model"""
    __tablename__ = 'service_tickets'
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('mechanics.id'), nullable=True)
    vehicle_info = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='pending')
    priority = db.Column(db.String(20), default='medium')
    estimated_cost = db.Column(db.Numeric(10, 2))
    actual_cost = db.Column(db.Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    customer = db.relationship('Customer', back_populates='service_tickets')
    mechanic = db.relationship('Mechanic', backref='assigned_tickets')
    
    def __repr__(self):
        return f'<ServiceTicket {self.id} - {self.status}>'
    
    def to_dict(self):
        """Convert service ticket to dictionary"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'mechanic_id': self.mechanic_id,
            'vehicle_info': self.vehicle_info,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'estimated_cost': float(self.estimated_cost) if self.estimated_cost else None,
            'actual_cost': float(self.actual_cost) if self.actual_cost else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }