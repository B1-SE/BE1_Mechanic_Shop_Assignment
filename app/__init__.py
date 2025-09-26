import os
from flask import Flask
from flasgger import Swagger
from config import config
from .extensions import db, ma, cors, jwt, limiter, cache


def create_app(config_name="production"):
    """
    Application factory.

    Creates and configures the Flask application, initializes extensions,
    and registers API blueprints.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # --- Initialize Extensions ---
    db.init_app(app)
    ma.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    cache.init_app(app, config={"CACHE_TYPE": "SimpleCache"})

    # --- Swagger/Flasgger Configuration ---
    # Use an environment variable for the host, defaulting to localhost for development.
    # On Render, you will set SWAGGER_HOST to your live API's base URL.
    swagger_host = os.environ.get("SWAGGER_HOST", "127.0.0.1:5000")

    swagger_template = {
        "swagger": "2.0",
        "info": {
            "title": "Mechanic Shop API",
            "description": "API for managing customers, mechanics, and service tickets.",
            "version": "1.0.0",
        },
        "host": swagger_host,
        "schemes": ["https" if "onrender.com" in swagger_host else "http"],
        "basePath": "/",
        "produces": ["application/json"],
    }
    Swagger(app, template=swagger_template)

    # --- Register Blueprints ---
    # This is the most critical missing step. You must register your API routes.
    from .api.customers import customers_bp
    from .api.mechanics import mechanics_bp
    
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')

    # --- Root and Health Check Routes ---
    @app.route("/")
    def index():
        """
        Root endpoint providing basic API information.
        ---
        responses:
          200:
            description: API Information
        """
        return {"message": "Welcome to the Mechanic Shop API!"}

    @app.route("/health")
    def health_check():
        """Health check endpoint."""
        return {"status": "ok"}

    return app