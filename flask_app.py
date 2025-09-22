"""
Main entry point for the Mechanic Shop Flask application.
"""
from app import create_app
from app.models import db

# Create the application
app = create_app('production')

with app.app_context():
    #db.drop_all()  # Uncomment to reset the database (use with caution)
    db.create_all()