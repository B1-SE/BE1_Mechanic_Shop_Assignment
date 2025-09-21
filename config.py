"""
Application configuration settings.
"""

import os
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Base configuration class."""
    
    # Basic Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SQLAlchemy config
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True
    
    # Application settings
    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    """Development configuration."""
    
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        f'sqlite:///{BASE_DIR}/instance/mechanic_shop_dev.db'


class TestingConfig(Config):
    """Testing configuration."""
    
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""
    
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}