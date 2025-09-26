"""
Customer routes for the mechanic shop application.
"""

from flask import Blueprint, request, jsonify
from app.extensions import db, limiter
from app.models.customer import Customer
from app.models.service_ticket import ServiceTicket
from app.schemas.service_ticket import service_tickets_schema
from app.schemas.customer import customer_schema, customers_schema, LoginResponseSchema
from app.utils.auth import generate_token, token_required
from app.utils.util import validate_email

# Create customers blueprint
customers_bp = Blueprint("customers", __name__)


@customers_bp.route("/", methods=["GET"])
@limiter.limit("100 per minute")
def get_all_customers():
    """
    Get all customers
    ---
    tags:
      - Customers
    summary: Retrieve a list of all customers.
    description: This endpoint retrieves all customers from the database.
    responses:
      200:
        description: A list of customers.
        schema:
          type: object
          properties:
            customers:
              type: array
              items:
                $ref: '#/definitions/Customer'
    """
    """Get all customers"""
    try:
        customers = Customer.query.all()
        result = customers_schema.dump(customers)

        return jsonify({"customers": result, "count": len(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customers_bp.route("/<int:customer_id>", methods=["GET"])
@limiter.limit("100 per minute")
def get_customer(customer_id):
    """
    Get a specific customer by ID
    ---
    tags:
      - Customers
    summary: Retrieve a single customer's details.
    parameters:
      - in: path
        name: customer_id
        type: integer
        required: true
    responses:
      200:
        description: Customer details.
      404:
        description: Customer not found.
    """
    """Get a specific customer"""
    try:
        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify(customer_schema.dump(customer)), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@customers_bp.route("/", methods=["POST"])
@limiter.limit("50 per minute")
def create_customer():
    """
    Create a new customer
    ---
    tags:
      - Customers
    summary: Register a new customer.
    parameters:
      - in: body
        name: body
        schema:
          $ref: '#/definitions/CustomerCreate'
    responses:
      201:
        description: Customer created successfully.
      400:
        description: Invalid input or email already exists.
    """
    """Create a new customer"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON or empty request body"}), 400

        # Validate required fields
        required_fields = ["first_name", "last_name", "email", "password"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        # Validate email format
        if not validate_email(data["email"]):
            return jsonify({"error": "Invalid email format"}), 400

        # Check if email already exists
        existing_customer = Customer.query.filter_by(email=data["email"]).first()
        if existing_customer:
            return jsonify({"error": "Email already exists"}), 400

        # Create new customer
        customer = Customer(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            phone_number=data.get("phone_number"),
            address=data.get("address"),
        )
        # Set the password, which is a required field
        customer.set_password(data["password"])

        # Save to database
        db.session.add(customer)
        db.session.commit()

        return jsonify(customer_schema.dump(customer)), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@customers_bp.route("/<int:customer_id>", methods=["PUT"])
@limiter.limit("50 per minute")
@token_required
def update_customer(current_customer, customer_id):
    """
    Update a customer
    ---
    tags:
      - Customers
    summary: Update an existing customer's details.
    security:
      - Bearer: []
    parameters:
      - in: path
        name: customer_id
        type: integer
        required: true
      - in: body
        name: body
        schema:
          $ref: '#/definitions/CustomerUpdate'
    responses:
      200:
        description: Customer updated successfully.
      403:
        description: Unauthorized to update this customer.
      404:
        description: Customer not found.
    """
    """Update a customer (requires authentication)"""
    try:
        # Check ownership inline
        if current_customer.id != customer_id:
            return jsonify({"error": "Unauthorized access"}), 403

        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        data = request.get_json()

        # Validate email format if provided
        if "email" in data and not validate_email(data["email"]):
            return jsonify({"error": "Invalid email format"}), 400

        # Update fields
        if "first_name" in data:
            customer.first_name = data["first_name"]
        if "last_name" in data:
            customer.last_name = data["last_name"]
        if "email" in data:
            # Check if new email already exists (for different customer)
            existing = Customer.query.filter_by(email=data["email"]).first()
            if existing and existing.id != customer_id:
                return jsonify({"error": "Email already exists"}), 409
            customer.email = data["email"]
        if "phone_number" in data:
            customer.phone_number = data["phone_number"]
        if "address" in data:
            customer.address = data["address"]
        if "password" in data:
            customer.set_password(data["password"])

        db.session.commit()
        return jsonify(customer_schema.dump(customer)), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
@limiter.limit("50 per minute")
@token_required
def delete_customer(current_customer, customer_id):
    """
    Delete a customer
    ---
    tags:
      - Customers
    summary: Delete a customer's account.
    security:
      - Bearer: []
    parameters:
      - in: path
        name: customer_id
        type: integer
        required: true
    responses:
      200:
        description: Customer deleted successfully.
    """
    """Delete a customer (requires authentication)"""
    try:
        # Check ownership inline
        if current_customer.id != customer_id:
            return jsonify({"error": "Unauthorized access"}), 403

        customer = db.session.get(Customer, customer_id)
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

        db.session.delete(customer)
        db.session.commit()

        return jsonify({"message": "Customer deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@customers_bp.route("/login", methods=["POST"])
@limiter.limit("50 per minute")
def login():
    """
    Customer Login
    ---
    tags:
      - Authentication
    summary: Authenticate a customer and receive a JWT token.
    parameters:
      - in: body
        name: body
        schema:
          $ref: '#/definitions/LoginCredentials'
    definitions:
      LoginCredentials:
        type: object
        required:
          - email
          - password
        properties:
          email:
            type: string
            format: email
            example: "john.doe@example.com"
          password:
            type: string
            example: "securepassword123"
    responses:
      200:
        description: Login successful.
      401:
        description: Invalid credentials.
    """
    """Customer login"""
    try:
        # Use silent=True to prevent an exception on an empty request body
        data = request.get_json(silent=True)

        if (
            not data
            or not data.get("email")
            or not data.get("password")
            or not isinstance(data["email"], str)
        ):
            return jsonify({"error": "Email and password required"}), 400

        customer = Customer.query.filter_by(email=data["email"]).first()

        if not customer:
            return jsonify({"error": "Invalid credentials"}), 401

        if not customer.password_hash:
            return (
                jsonify(
                    {"error": "Account not properly configured for password login"}
                ),
                401,
            )

        if not customer.check_password(data["password"]):
            return jsonify({"error": "Invalid credentials"}), 401

        # Generate proper JWT token - fix this line to include email
        token = generate_token(customer.id, customer.email)

        # Use the new schema for a consistent response
        login_response_schema = LoginResponseSchema()
        response_data = {
            "message": "Login successful",
            "customer": customer,
            "token": token,
        }
        return login_response_schema.dump(response_data), 200

    except Exception as e:
        print(f"Login error: {str(e)}")  # Debug logging
        return jsonify({"error": f"Login failed: {str(e)}"}), 500


@customers_bp.route("/my-tickets", methods=["GET"])
@limiter.limit("100 per minute")
@token_required
def get_my_tickets(current_customer):
    """
    Get my service tickets
    ---
    tags:
      - Customers
    summary: Get all service tickets for the authenticated customer.
    description: Requires a valid JWT token. Returns a list of service tickets associated with the logged-in customer.
    security:
      - Bearer: []
    responses:
      200:
        description: Service tickets retrieved successfully.
      401:
        description: Unauthorized, token is missing or invalid.
    """
    try:
        tickets = ServiceTicket.query.filter_by(customer_id=current_customer.id).all()
        result = service_tickets_schema.dump(tickets)
        return jsonify({"tickets": result, "count": len(result)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
