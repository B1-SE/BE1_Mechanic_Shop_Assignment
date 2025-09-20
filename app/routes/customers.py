"""
Customer routes for the mechanic shop API.
"""

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from app.extensions import db, limiter, cache
from app.models.customer import Customer
from app.schemas.customer import customer_schema, customers_schema, login_schema
from app.utils.auth import encode_token, token_required

# Create customer blueprint
customers_bp = Blueprint('customers', __name__)


@customers_bp.route('/', methods=['POST'])
@limiter.limit("5 per minute")  # Rate limit: max 5 customer creations per minute per IP
def create_customer():
    """
    Create a new customer.
    
    Rate Limited: 5 requests per minute per IP address
    WHY: Prevents spam account creation, protects against automated abuse,
    and reduces load on the database from excessive customer registrations.
    """
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400

        # Validate and load the data
        customer_data = customer_schema.load(json_data)
        
        # Check if email already exists
        existing_customer = Customer.query.filter_by(email=customer_data['email']).first()
        if existing_customer:
            return jsonify({"error": "Email already associated with another account"}), 400
        
        # Create new customer from the dictionary
        new_customer = Customer(**customer_data)
        db.session.add(new_customer)
        db.session.commit()

        return jsonify(customer_schema.dump(new_customer)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400


@customers_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate customer and return JWT token.
    
    Expects JSON with email and password.
    Returns JWT token if credentials are valid.
    """
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'No input data provided'}), 400

        # Validate login data
        login_data = login_schema.load(json_data)
        
        # Find customer by email
        customer = Customer.query.filter_by(email=login_data['email']).first()
        
        if not customer or not customer.check_password(login_data['password']):
            return jsonify({
                'error': 'Invalid credentials',
                'message': 'Email or password is incorrect'
            }), 401
        
        # Generate JWT token
        token = encode_token(customer.id)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'customer': customer_schema.dump(customer)
        }), 200
        
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        return jsonify({'error': 'Login failed', 'message': str(e)}), 500


@customers_bp.route('/my-tickets', methods=['GET'])
@token_required
def get_my_tickets(customer_id):
    """
    Get all service tickets for the authenticated customer.
    
    Requires Bearer token authorization.
    The customer_id is automatically provided by the @token_required decorator.
    """
    try:
        from app.models.service_ticket import ServiceTicket
        from app.schemas.service_ticket import service_tickets_schema
        
        # Query service tickets for this customer
        tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
        
        return jsonify({
            'message': f'Found {len(tickets)} service tickets',
            'tickets': service_tickets_schema.dump(tickets)
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve tickets', 'message': str(e)}), 500


@customers_bp.route('/', methods=['GET'])
def get_customers():
    """
    Get all customers with advanced pagination, sorting, and filtering.
    
    Query Parameters:
    - page: Page number (default: 1)
    - per_page: Items per page (default: 10, max: 100)
    - sort_by: Sort field (id, first_name, last_name, email, created_at)
    - order: Sort order (asc, desc) (default: asc)
    - search: Search term for name or email
    - email: Filter by exact email
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)  # Max 100 items per page
        sort_by = request.args.get('sort_by', 'id')
        order = request.args.get('order', 'asc').lower()
        search = request.args.get('search', '').strip()
        email_filter = request.args.get('email', '').strip()
        
        # Validate sort_by parameter
        valid_sort_fields = ['id', 'first_name', 'last_name', 'email']
        if sort_by not in valid_sort_fields:
            return jsonify({
                'error': 'Invalid sort field',
                'message': f'sort_by must be one of: {", ".join(valid_sort_fields)}'
            }), 400
        
        # Validate order parameter
        if order not in ['asc', 'desc']:
            return jsonify({
                'error': 'Invalid order',
                'message': 'order must be "asc" or "desc"'
            }), 400
        
        # Start building query
        query = Customer.query
        
        # Apply search filter (searches in first_name, last_name, and email)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Customer.first_name.ilike(search_term),
                    Customer.last_name.ilike(search_term),
                    Customer.email.ilike(search_term)
                )
            )
        
        # Apply email filter
        if email_filter:
            query = query.filter(Customer.email.ilike(f"%{email_filter}%"))
        
        # Apply sorting
        sort_column = getattr(Customer, sort_by)
        if order == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        paginated_customers = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Prepare response
        response_data = {
            'customers': customers_schema.dump(paginated_customers.items),
            'pagination': {
                'page': paginated_customers.page,
                'per_page': paginated_customers.per_page,
                'total': paginated_customers.total,
                'pages': paginated_customers.pages,
                'has_next': paginated_customers.has_next,
                'has_prev': paginated_customers.has_prev,
                'next_page': paginated_customers.next_num if paginated_customers.has_next else None,
                'prev_page': paginated_customers.prev_num if paginated_customers.has_prev else None
            },
            'filters_applied': {
                'search': search if search else None,
                'email': email_filter if email_filter else None,
                'sort_by': sort_by,
                'order': order
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve customers', 'message': str(e)}), 500


@customers_bp.route('/<int:customer_id>', methods=['GET'])
def get_customer(customer_id):
    """Get a single customer by ID."""
    customer = db.session.get(Customer, customer_id)
    
    if customer:
        return jsonify(customer_schema.dump(customer)), 200
    
    return jsonify({"error": "Customer not found"}), 404


@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@token_required
def update_customer(auth_customer_id, customer_id):
    """
    Update a customer by ID. Requires authentication.
    
    Customers can only update their own information.
    """
    # Ensure customer can only update their own information
    if auth_customer_id != customer_id:
        return jsonify({
            'error': 'Unauthorized',
            'message': 'You can only update your own information'
        }), 403
    
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'message': 'No input data provided'}), 400
            
        customer_data = customer_schema.load(json_data, partial=True)
        
        # Update customer attributes
        for key, value in customer_data.items():
            setattr(customer, key, value)

        db.session.commit()
        return jsonify(customer_schema.dump(customer)), 200
    except ValidationError as err:
        return jsonify(err.messages), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 400


@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
@token_required
def delete_customer(auth_customer_id, customer_id):
    """
    Delete a customer by ID. Requires authentication.
    
    Customers can only delete their own account.
    """
    # Ensure customer can only delete their own account
    if auth_customer_id != customer_id:
        return jsonify({
            'error': 'Unauthorized',
            'message': 'You can only delete your own account'
        }), 403
    
    customer = db.session.get(Customer, customer_id)
    
    if not customer:
        return jsonify({"error": "Customer not found"}), 404
    
    try:
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Customer deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500