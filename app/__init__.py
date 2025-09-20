"""
Application factory for the mechanic shop Flask application.
"""

from flask import Flask, send_from_directory, jsonify
from sqlalchemy import inspect
from datetime import datetime
import os

from config import config
from app.extensions import db, ma, limiter, cache


def create_app(config_name=None):
    """
    Create and configure the Flask application.
    
    Args:
        config_name (str): Configuration name ('development', 'testing', 'production')
                          If None, defaults to 'development'
    
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = 'development'
    
    app.config.from_object(config[config_name])
    
    # Configure caching (using simple in-memory cache for development)
    app.config['CACHE_TYPE'] = 'simple'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300  # 5 minutes default cache timeout
    
    # Initialize extensions
    db.init_app(app)
    ma.init_app(app)
    limiter.init_app(app)  # Initialize rate limiter
    cache.init_app(app)    # Initialize cache
    
    # Register blueprints
    register_blueprints(app)
    
    # Create database tables
    with app.app_context():
        inspector = inspect(db.engine)
        # Import models to ensure they are registered with SQLAlchemy
        from app.models import Customer, ServiceTicket, Mechanic, Inventory
        
        if not inspector.has_table('customers'):
            print("Creating database tables...")
            db.create_all()
            print("Database tables created successfully!")
    
    return app


def register_blueprints(app):
    """Register application blueprints."""
    from app.routes import customers_bp
    from app.blueprints.mechanics import mechanics_bp
    from app.blueprints.service_tickets import service_tickets_bp
    from app.blueprints.inventory import inventory_bp
    
    # Register blueprints with URL prefixes
    app.register_blueprint(customers_bp, url_prefix='/customers')
    app.register_blueprint(mechanics_bp, url_prefix='/mechanics')
    app.register_blueprint(service_tickets_bp, url_prefix='/service-tickets')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Simple health check endpoint."""
        return {'status': 'healthy', 'message': 'Mechanic Shop API is running'}, 200
    
    # Favicon endpoint to serve the actual favicon.ico file
    @app.route('/favicon.ico')
    def favicon():
        """Serve the favicon.ico file from the static directory."""
        static_dir = os.path.join(app.root_path, 'static')
        try:
            return send_from_directory(static_dir, 'favicon.ico', mimetype='image/vnd.microsoft.icon')
        except FileNotFoundError:
            # Fallback to empty response if favicon not found
            return '', 204
    
    # Optional: General static file serving route
    @app.route('/static/<path:filename>')
    def static_files(filename):
        """Serve static files from the static directory."""
        static_dir = os.path.join(app.root_path, 'static')
        return send_from_directory(static_dir, filename)
    
    # Rate limiting demonstration endpoint
    @app.route('/test-rate-limit')
    @limiter.limit("5 per minute")
    def test_rate_limit():
        """
        Test endpoint to demonstrate rate limiting.
        Limited to 5 requests per minute per IP.
        """
        return jsonify({
            'message': 'Rate limiting is working!',
            'limit': '5 requests per minute',
            'timestamp': datetime.now().isoformat()
        }), 200
    
    @app.route('/')
    def index():
        """API information endpoint."""
        return {
            'message': 'Welcome to the Mechanic Shop API',
            'version': '1.0.0',
            'endpoints': {
                'customers': '/customers',
                'mechanics': '/mechanics',
                'service_tickets': '/service-tickets',
                'inventory': '/inventory',
                'health': '/health'
            }
        }, 200