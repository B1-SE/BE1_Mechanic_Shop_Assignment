"""
Application factory for the mechanic shop Flask application.
"""

from flask import Flask, send_from_directory, jsonify
from flask import Blueprint
from sqlalchemy import inspect
from datetime import datetime
import os
from config import config
from app.extensions import db, ma, limiter, cache, jwt, cors

# Global variable to track if swagger is already set up
_swagger_registered = False


def create_app(config_class=None):
    """
    Create and configure the Flask application.

    Args:
        config_class: Configuration class object
                     If None, defaults to 'development' config

    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    # Ensure we are using a config object, not a class
    if config_class is None:
        app.config.from_object(config["development"]())
    else:
        app.config.from_object(config_class)

    # Ensure the instance folder exists for SQLite databases
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass  # Ignore errors if the folder already exists or can't be created
    # Configure caching (using simple in-memory cache for development)
    app.config["CACHE_TYPE"] = "simple"
    app.config["CACHE_DEFAULT_TIMEOUT"] = 300  # 5 minutes default cache timeout

    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)  # Initialize rate limiter
    cache.init_app(app)  # Initialize cache
    jwt.init_app(app)
    cors.init_app(app)

    # Register blueprints
    register_blueprints(app)

    # Register additional routes (like /health, /)
    register_additional_routes(app)

    # Create database tables
    with app.app_context():
        inspector = inspect(db.engine)
        # Import models to ensure they are registered with SQLAlchemy
        try:
            from app.models import (
                customer,  # noqa: F401
                service_ticket,  # noqa: F401
                mechanic,  # noqa: F401
                inventory,  # noqa: F401
            )
        except ImportError as e:
            print(f"Warning: Could not import some models: {e}")

        if not inspector.has_table("customers"):
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully!")

    # Only register Swagger in non-testing environments
    if not app.config.get("TESTING", False):
        setup_swagger(app)

    return app


def setup_swagger(app):
    """Setup Swagger documentation"""
    global _swagger_registered

    if _swagger_registered:
        return

    try:
        # Use flasgger instead of flask_swagger
        from flasgger import Swagger

        host = "localhost:5000"
        schemes = ["http"]
        if not app.config.get("DEBUG", False):
            host = (
                os.environ.get("RENDER_EXTERNAL_HOSTNAME")
                or "mechanic-shop.onrender.com"
            )
            schemes = ["https"]

        swagger_template = {
            "swagger": "2.0",
            "info": {
                "title": "Mechanic Shop Management API",
                "description": (
                    "A comprehensive API for managing a mechanic shop's "
                    "operations including customers, mechanics, service "
                    "tickets, inventory, and memberships."
                ),
                "version": "1.0.0",
                "contact": {
                    "name": "API Support",
                    "email": "support@mechanicshop.com",
                },
            },
            "host": host,
            "basePath": "/",
            "schemes": schemes,
            "securityDefinitions": {
                "Bearer": {
                    "type": "apiKey",
                    "name": "Authorization",
                    "in": "header",
                    "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'",
                }
            },
            "tags": [
                {"name": "customers", "description": "Customer management operations"},
                {"name": "mechanics", "description": "Mechanic management operations"},
                {
                    "name": "service-tickets",
                    "description": "Service ticket management operations",
                },
                {"name": "inventory", "description": "Inventory management operations"},
                {"name": "members", "description": "Membership management operations"},
                {
                    "name": "calculations",
                    "description": "Mathematical calculation operations",
                },
                {
                    "name": "General",
                    "description": "General API and health-check endpoints",
                },
            ],
        }

        Swagger(app, template=swagger_template)
        _swagger_registered = True

    except ImportError:
        # Swagger packages not installed, skip swagger setup
        pass
    except Exception as e:
        print(f"Warning: Could not set up Swagger: {e}")


def register_blueprints(app):
    """Register application blueprints"""
    import importlib

    blueprints_to_register = [
        ("calculations", "/calculations"),
        ("customers", "/customers"),
        ("inventory", "/inventory"),
        ("mechanics", "/mechanics"),
        ("service_tickets", "/service-tickets"),
    ]

    for bp_name, url_prefix in blueprints_to_register:
        try:
            module = importlib.import_module(f"app.routes.{bp_name}")
            blueprint = getattr(module, f"{bp_name}_bp")
            app.register_blueprint(blueprint, url_prefix=url_prefix)
        except (ImportError, AttributeError) as e:
            print(f"Warning: Could not register blueprint '{bp_name}': {e}")

    # Create members blueprint as alias to customers - FIXED parameter handling
    try:
        members_bp = Blueprint("members", __name__)

        # Register members routes that delegate to customers
        @members_bp.route("/", methods=["GET"])
        def get_members():
            from app.routes.customers import get_all_customers

            return get_all_customers()

        @members_bp.route("/", methods=["POST"])
        def create_member():
            from app.routes.customers import create_customer

            return create_customer()

        @members_bp.route("/<int:member_id>", methods=["GET"])
        def get_member(member_id):
            from app.routes.customers import get_customer

            return get_customer(member_id)

        @members_bp.route("/<int:member_id>", methods=["PUT"])
        def update_member(member_id):
            from app.routes.customers import update_customer

            # The update_customer function expects `current_customer` from the token
            # The token_required decorator will handle this when the request is processed
            return update_customer(customer_id=member_id)

        @members_bp.route("/<int:member_id>", methods=["DELETE"])
        def delete_member(member_id):
            from app.routes.customers import delete_customer

            return delete_customer(customer_id=member_id)

        @members_bp.route("/login", methods=["POST"])
        def member_login():
            from app.routes.customers import login

            return login()

        app.register_blueprint(members_bp, url_prefix="/members")

    except ImportError as e:
        print(f"Warning: Could not create members blueprint: {e}")


def register_additional_routes(app):
    """Register additional application routes"""

    # API root endpoint
    @app.route("/")
    def index():
        """
        Get API Information
        ---
        tags:
          - General
        summary: Get general information about the API and available endpoints.
        description: Returns a welcome message and a list of available API endpoints.
        responses:
          200:
            description: API information retrieved successfully.
        """
        return (
            jsonify(
                {
                    "message": "Welcome to the Mechanic Shop API",
                    "version": "1.0.0",
                    "endpoints": {
                        "customers": "/customers",
                        "mechanics": "/mechanics",
                        "service_tickets": "/service-tickets",
                        "inventory": "/inventory",
                        "members": "/members",
                        "calculations": "/calculations",
                        "health": "/health",
                        "api_docs": "/apidocs",
                    },
                }
            ),
            200,
        )

    # Health check endpoint
    @app.route("/health")
    def health_check():
        """
        Health Check
        ---
        tags:
          - General
        summary: Check if the API is running and healthy.
        description: Simple health check endpoint.
        responses:
          200:
            description: API is healthy.
        """
        return (
            jsonify(
                {
                    "status": "healthy",
                    "message": "Mechanic Shop API is running",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    # Rate limiting demonstration endpoint
    @app.route("/test-rate-limit")
    @limiter.limit("5 per minute")
    def test_rate_limit():
        """
        Test Rate Limiting
        ---
        tags:
          - General
        summary: Test endpoint to demonstrate rate limiting.
        description: Limited to 5 requests per minute per IP.
        responses:
          200:
            description: Request successful.
          429:
            description: Too many requests.
        """
        return (
            jsonify(
                {
                    "message": "Rate limiting is working!",
                    "limit": "5 requests per minute",
                    "timestamp": datetime.now().isoformat(),
                }
            ),
            200,
        )

    # Favicon endpoint
    @app.route("/favicon.ico")
    def favicon():
        """Serve the favicon.ico file from the static directory."""
        static_dir = os.path.join(app.root_path, "static")
        try:
            return send_from_directory(
                static_dir, "favicon.ico", mimetype="image/vnd.microsoft.icon"
            )
        except FileNotFoundError:
            # Fallback to empty response if favicon not found
            return "", 204

    # Optional: General static file serving route
    @app.route("/static/<path:filename>")
    def static_files(filename):
        """Serve static files from the static directory."""
        static_dir = os.path.join(app.root_path, "static")
        return send_from_directory(static_dir, filename)

    # Product data endpoint (example implementation)
    @app.route("/api/products", methods=["GET"])
    def get_products():
        """Get list of products"""
        # Sample response structure
        return {
            "Version": "1.0.0",
            "StatusCode": 200,
            "ApiRequestId": "unique-request-id",
            "Result": [
                {
                    "id": 1,
                    "name": "Product 1",
                    "description": "Description for product 1",
                    "price": 9.99,
                    "currency": "USD",
                },
                {
                    "id": 2,
                    "name": "Product 2",
                    "description": "Description for product 2",
                    "price": 19.99,
                    "currency": "USD",
                },
            ],
        }, 200

    return app
