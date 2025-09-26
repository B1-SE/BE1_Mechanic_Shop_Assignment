"""
Authentication-related utilities, including token generation and validation.
"""

from functools import wraps
from flask import request, jsonify, current_app
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.models.customer import Customer
from app.models.mechanic import Mechanic


def encode_token(customer_id):
    """
    Generates a JWT token for a given customer ID.

    Args:
        customer_id (int): The ID of the customer to encode in the token.

    Returns:
        str: The encoded token.
    """
    payload = {
        "exp": datetime.utcnow() + timedelta(days=1),  # Token expires in 1 day
        "iat": datetime.utcnow(),  # Issued at time
        "sub": customer_id,  # Subject of the token (customer_id)
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def encode_mechanic_token(mechanic_id):
    """
    Generates a JWT token for a given mechanic ID.

    Args:
        mechanic_id (int): The ID of the mechanic to encode in the token.

    Returns:
        str: The encoded JWT token with a 'mechanic' role.
    """
    payload = {
        "exp": datetime.utcnow() + timedelta(days=1),
        "iat": datetime.utcnow(),
        "sub": mechanic_id,
        "role": "mechanic",  # Add role to distinguish from customer tokens
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def token_required(f):
    """
    Decorator to protect routes that require a valid token.

    Validates the 'Authorization' header for a 'Bearer' token, decodes it,
    and passes the customer_id to the decorated function.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        # Check for token in the 'Authorization' header
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            # Decode the token using the secret key
            payload = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            customer_id = payload["sub"]

            # Ensure the customer exists
            current_customer = Customer.query.get(customer_id)
            if not current_customer:
                return jsonify({"message": "User not found!"}), 401

        except JWTError as e:
            return jsonify({"message": f"Token is invalid! {str(e)}"}), 401
        except Exception as e:
            return jsonify({"message": f"An error occurred: {str(e)}"}), 500

        # Pass the customer_id to the decorated route function
        return f(customer_id=customer_id, *args, **kwargs)

    return decorated_function


def mechanic_token_required(f):
    """
    Decorator to protect routes that require a valid mechanic token.

    Validates the 'Authorization' header for a 'Bearer' token, decodes it,
    ensures the user has the 'mechanic' role, and passes the mechanic_id
    to the decorated function.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"message": "Token is missing!"}), 401

        try:
            payload = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )

            # Check for mechanic role
            if payload.get("role") != "mechanic":
                return jsonify({"message": "Mechanic access required!"}), 403

            mechanic_id = payload["sub"]

            # Ensure the mechanic exists
            current_mechanic = Mechanic.query.get(mechanic_id)
            if not current_mechanic:
                return jsonify({"message": "Mechanic not found!"}), 401

        except JWTError as e:
            return jsonify({"message": f"Token is invalid! {str(e)}"}), 401
        except Exception as e:
            return jsonify({"message": f"An error occurred: {str(e)}"}), 500

        return f(mechanic_id=mechanic_id, *args, **kwargs)

    return decorated_function