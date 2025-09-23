#!/bin/bash
# Force install the exact SQLAlchemy version that works with Python 3.13
echo "Upgrading SQLAlchemy to Python 3.13 compatible version..."
pip install --upgrade --force-reinstall SQLAlchemy==2.0.43 Flask==3.1.0
echo "Starting application..."
gunicorn flask_app:app