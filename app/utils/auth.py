"""
Authentication utilities for JWT token handling.
"""

import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from app.models.customer import Customer


def encode_token(customer_id):
    """
    Encode a JWT token for a specific customer.
    
    Args:
        customer_id (int): The customer's unique ID
        
    Returns:
        str: Encoded JWT token
    """
    try:
        payload = {
            'exp': datetime.utcnow() + timedelta(hours=24),  # Token expires in 24 hours
            'iat': datetime.utcnow(),  # Token issued at
            'sub': str(customer_id)  # Subject (customer ID) - must be string for PyJWT
        }
        token = jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return token
    except Exception as e:
        return str(e)


def decode_token(token):
    """
    Decode a JWT token and extract customer ID.
    
    Args:
        token (str): JWT token to decode
        
    Returns:
        int or str: Customer ID if valid, error message if invalid
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        # Convert string customer_id back to integer
        return int(payload['sub'])
    except jwt.ExpiredSignatureError:
        return 'Token has expired'
    except jwt.InvalidTokenError:
        return 'Invalid token'
    except Exception as e:
        return f'Token error: {str(e)}'


def token_required(f):
    """
    Decorator that validates JWT tokens and injects customer_id into the decorated function.
    
    Usage:
        @token_required
        def protected_route(customer_id):
            # customer_id is automatically provided by the decorator
            pass
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                # Expected format: "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({
                    'error': 'Invalid authorization header format',
                    'message': 'Expected format: Bearer <token>'
                }), 401
        
        if not token:
            return jsonify({
                'error': 'Token is missing',
                'message': 'Please provide a valid authorization token'
            }), 401
        
        # Decode token and get customer ID
        customer_id = decode_token(token)
        
        if isinstance(customer_id, str):  # Error message returned
            return jsonify({
                'error': 'Token validation failed',
                'message': customer_id
            }), 401
        
        # Verify customer exists in database
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({
                'error': 'Invalid customer',
                'message': 'Customer associated with token not found'
            }), 401
        
        # Pass customer_id to the decorated function
        return f(customer_id, *args, **kwargs)
    
    return decorated_function