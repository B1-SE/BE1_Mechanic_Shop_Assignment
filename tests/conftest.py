git checkout -b fix-unused-import"""
Pytest fixtures for the Flask application.

This file provides reusable components for testing, such as the Flask app
instance and a test client, ensuring a clean and consistent test environment.
"""

import pytest
from app import create_app
from app.extensions import db
from config import config


@pytest.fixture(scope="module")
def app():
    """Create and configure a new app instance for each test module."""
    # Create a test app instance
    app = create_app(config["testing"])

    # Establish an application context
    with app.app_context():
        # Create the database and the database table(s)
        db.create_all()

        yield app  # this is where the testing happens!

        # Tearing down the database
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope="module")
def client(app):
    """A test client for the app."""
    return app.test_client()