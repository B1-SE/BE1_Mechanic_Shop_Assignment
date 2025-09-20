"""
Flask extensions initialization.
Extensions are initialized here to avoid circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

# Initialize extensions
db = SQLAlchemy()
ma = Marshmallow()

# Rate limiting - protects against abuse and DoS attacks
limiter = Limiter(
    key_func=get_remote_address,  # Rate limit by IP address
    default_limits=["1000 per hour", "100 per minute"]  # Default limits for all routes
)

# Caching - improves performance by storing frequently accessed data
cache = Cache()