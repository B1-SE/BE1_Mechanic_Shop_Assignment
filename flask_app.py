"""
Main entry point for the Mechanic Shop Flask application.
"""

from app import create_app
from app.extensions import db
from config import config

# Create the application
app = create_app(config["production"])

with app.app_context():
    # db.drop_all()  # Uncomment to reset the database (use with caution)
    db.create_all()
