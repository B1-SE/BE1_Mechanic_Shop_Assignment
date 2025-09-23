#!/bin/bash
# Force clear any cached packages and get the latest compatible versions
pip install --upgrade --force-reinstall SQLAlchemy Flask Flask-SQLAlchemy
# Start the application
gunicorn flask_app:app