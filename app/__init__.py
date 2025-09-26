from flask import Flask
from config import config

def create_app(config_name='production'):
    """Application factory."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions here
    # db.init_app(app)
    # migrate.init_app(app, db)

    # Register blueprints here

    return app