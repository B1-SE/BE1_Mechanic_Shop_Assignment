"""
Routes package for the mechanic shop application.
"""

from .customers import customers_bp
from .service_tickets import service_tickets_bp
from .calculations import calculations_bp

# Export all blueprints
__all__ = ["customers_bp", "service_tickets_bp", "calculations_bp"]
