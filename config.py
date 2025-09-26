import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super secret secrets'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    # Use an in-memory SQLite database for fast, isolated tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # Disable CSRF protection in tests for simplicity
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration."""
    # Render provides a DATABASE_URL environment variable
    # for the PostgreSQL database.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    # You can add other production-specific settings here.

config = {'development': DevelopmentConfig, 'production': ProductionConfig, 'testing': TestingConfig}