"""
Application configuration settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent


class Config:
    """Base configuration class."""

    # Basic Flask config - using environment variable
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"

    # SQLAlchemy config
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    # Application settings
    JSON_SORT_KEYS = False

    # Rate limiting config - using environment variable for Redis
    RATELIMIT_STORAGE_URI = os.environ.get("REDIS_URL") or "memory://"


class DevelopmentConfig(Config):
    """Development configuration."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DEV_DATABASE_URL")
        or f"sqlite:///{BASE_DIR}/instance/mechanic_shop_dev.db"
    )


class TestingConfig(Config):
    """Testing configuration."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration."""

    DEBUG = False

    # For production, the database URL must be set via an environment variable.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # Fail fast if the production database URL is not configured.
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("No DATABASE_URL set for production environment")


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
