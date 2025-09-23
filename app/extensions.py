"""
Extensions for the mechanic shop application.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Initialize extensions
db = SQLAlchemy()
ma = Marshmallow()
limiter = Limiter(key_func=get_remote_address, default_limits=["1000 per hour"])
cache = Cache()
jwt = JWTManager()
cors = CORS()
