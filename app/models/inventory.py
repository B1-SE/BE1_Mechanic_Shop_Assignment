"""
Inventory model for the mechanic shop application.
"""

from app.extensions import db
from datetime import datetime, timezone


class InventoryItem(db.Model):
    """Inventory item model"""

    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    supplier = db.Column(db.String(100))
    category = db.Column(db.String(50))
    reorder_level = db.Column(db.Integer, default=5)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<InventoryItem {self.name}>"

    def to_dict(self):
        """Convert inventory item to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "quantity": self.quantity,
            "price": float(self.price),
            "supplier": self.supplier,
            "category": self.category,
            "reorder_level": self.reorder_level,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
