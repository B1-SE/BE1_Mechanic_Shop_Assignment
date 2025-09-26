"""
WSGI entry point for the Flask application.

This script is used by Gunicorn to serve the application in production.
It creates the Flask app instance using the 'production' configuration.
"""

import os
from app import create_app
from config import config

# Get the configuration name from the environment variable.
# Default to 'production' for safety in production environments.
config_name = os.getenv("FLASK_ENV", "production")

application = create_app(config[config_name])
