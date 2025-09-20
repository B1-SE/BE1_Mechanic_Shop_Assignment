#!/usr/bin/env python3
"""
Main entry point for the Mechanic Shop Flask application.
"""

import os
from app import create_app

# Create the application
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Development server settings
    debug_mode = app.config.get('DEBUG', False)
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '127.0.0.1')
    
    print(f"Starting Mechanic Shop API...")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Debug mode: {debug_mode}")
    print(f"Server: http://{host}:{port}")
    
    app.run(host=host, port=port, debug=debug_mode)