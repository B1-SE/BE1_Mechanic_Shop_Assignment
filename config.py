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

    # For production, prefer environment variables but fallback to SQLite
    database_url = os.environ.get("SQLALCHEMY_DATABASE_URI") or os.environ.get(
        "DATABASE_URL"
    )

    # If no database URL is provided or if it's a local PostgreSQL URL, use SQLite
    if not database_url or "localhost" in database_url or "127.0.0.1" in database_url:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{BASE_DIR}/instance/mechanic_shop_prod.db"
    else:
        SQLALCHEMY_DATABASE_URI = database_url


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
