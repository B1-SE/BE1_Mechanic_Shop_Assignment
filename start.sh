#!/bin/bash
# Force clear any cached packages
pip install --upgrade --force-reinstall SQLAlchemy==2.0.30 Flask==3.0.3
# Start the application
gunicorn flask_app:app