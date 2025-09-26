"""
WSGI entry point for the Flask application.

This script is used by Gunicorn to serve the application in production.
It creates the Flask app instance using the 'production' configuration.
"""

from app import create_app
from config import config

# Create the application instance with the production configuration
application = create_app(config["production"])

# The 'application' variable is what Gunicorn looks for by default.