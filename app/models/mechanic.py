"""
Mechanic model for the mechanic shop application.
"""

from app.extensions import db
from datetime import datetime, timezone


class Mechanic(db.Model):
    """Mechanic model representing employees who perform vehicle services."""
    
    __tablename__ = 'mechanics'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    salary = db.Column(db.Numeric(10, 2))
    hire_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    specializations = db.Column(db.Text)  # JSON string of specializations
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Mechanic {self.name}>"
    
    def to_dict(self):
        """Convert mechanic to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'salary': float(self.salary) if self.salary else None,
            'created_at': self.created_at.isoformat() if hasattr(self, 'created_at') and self.created_at else None,
            'updated_at': self.updated_at.isoformat() if hasattr(self, 'updated_at') and self.updated_at else None
        }