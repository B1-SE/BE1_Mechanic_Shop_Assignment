"""
Authentication utilities for the mechanic shop application.
"""

import jwt
import os
from datetime import datetime, timedelta, timezone
from flask import jsonify, request
from functools import wraps


def generate_token(customer_id, email):
    """Generate a JWT token for a customer"""
    payload = {
        "customer_id": customer_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        "iat": datetime.now(timezone.utc),
    }

    # Use the application's configured secret key
    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key:
        raise ValueError("SECRET_KEY environment variable not set")
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token


def verify_token(token):
    """Verify and decode a JWT token"""
    try:
        secret_key = os.environ.get("SECRET_KEY")
        if not secret_key:
            raise ValueError("SECRET_KEY environment variable not set")
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """Decorator for routes that require authentication"""

    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Check for token in Authorization header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({"error": "Invalid token format"}), 401

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        # Import here to avoid circular dependency
        from app.models.customer import Customer
        from app.extensions import db

        # Verify token
        payload = verify_token(token)
        if payload is None:
            return jsonify({"error": "Token is invalid or expired"}), 401

        # Get customer from token - use db.session.get instead of query.get
        customer = db.session.get(Customer, payload["customer_id"])
        if not customer:
            return jsonify({"error": "Customer not found"}), 401

        # Pass customer to the route
        return f(current_customer=customer, *args, **kwargs)

    return decorated


def check_customer_ownership(customer_id):
    """Check if the current customer owns the resource"""

    def decorator(f):
        @wraps(f)
        def decorated(current_customer, *args, **kwargs):
            # Extract customer_id from route parameters
            route_customer_id = kwargs.get("customer_id")
            if route_customer_id and current_customer.id != route_customer_id:
                return jsonify({"error": "Access denied"}), 403
            return f(current_customer=current_customer, *args, **kwargs)

        return decorated

    return decorator
