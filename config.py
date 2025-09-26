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

    # Production database URL must be set via an environment variable.
    # Fallback to a local SQLite database for simplicity if not provided.
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL")
        or f"sqlite:///{BASE_DIR}/instance/mechanic_shop_prod.db"
    )

    # Ensure the instance folder exists for the production SQLite database
    # This is important for when Gunicorn or other services run the app.
    try:
        os.makedirs(f"{BASE_DIR}/instance", exist_ok=True)
    except OSError:
        pass


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
