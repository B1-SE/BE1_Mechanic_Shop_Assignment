"""
Main entry point for the Flask application.

This script creates and runs the Flask app using the application factory pattern.
It ensures the app is configured correctly based on environment variables.
"""

import os
from app import create_app
from config import config

# Get the configuration name from the environment variable or default to 'development'
config_name = os.getenv("FLASK_ENV", "default")  # Ensure a valid config is selected, falling back to default if the env var is invalid
# Ensure a valid config is selected, falling back to default if the env var is invalid
app_config = config.get(config_name, config["default"])
app = create_app(app_config)

if __name__ == "__main__":
    # Run the app. The host is set to '0.0.0.0' to be accessible on your network.
    app.run(host="0.0.0.0")