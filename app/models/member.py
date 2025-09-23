"""
Member model for the mechanic shop application.
"""

from app.extensions import db
from datetime import datetime, timezone


class Member(db.Model):
    """Member model for customer membership program"""

    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(
        db.Integer, db.ForeignKey("customers.id"), nullable=False, unique=True
    )
    membership_type = db.Column(db.String(50), default="basic")  # basic, premium, vip
    start_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    end_date = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relationship
    customer = db.relationship("Customer", backref="membership")

    def __repr__(self):
        return f"<Member {self.customer_id} - {self.membership_type}>"

    def to_dict(self):
        """Convert member to dictionary"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "membership_type": self.membership_type,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "is_active": self.is_active,
            "points": self.points,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
