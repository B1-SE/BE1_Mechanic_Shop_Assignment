"""
General utility functions for the mechanic shop application.
"""

import re
from typing import Any, Dict
import random
from datetime import datetime
from flask import jsonify


def validate_email(email: str) -> bool:
    """
    Validate email format using regex.

    Args:
        email: Email string to validate

    Returns:
        bool: True if valid email format, False otherwise
    """
    if not email:
        return False

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number string to validate

    Returns:
        bool: True if valid phone format, False otherwise
    """
    if not phone:
        return False

    # Remove all non-digit characters
    digits_only = re.sub(r"\D", "", phone)

    # Check if it's a valid length (10 or 11 digits)
    return len(digits_only) in [10, 11]


def format_currency(amount: float) -> str:
    """
    Format amount as currency string.

    Args:
        amount: Amount to format

    Returns:
        str: Formatted currency string
    """
    if amount is None:
        return "$0.00"
    return f"${amount:.2f}"


def sanitize_string(text: str, max_length: int = 255) -> str:
    """
    Sanitize and truncate string input.

    Args:
        text: Text to sanitize
        max_length: Maximum allowed length

    Returns:
        str: Sanitized text
    """
    if not text:
        return ""

    # Remove leading/trailing whitespace and limit length
    sanitized = text.strip()[:max_length]
    return sanitized


def paginate_results(query, page: int = 1, per_page: int = 10):
    """
    Paginate database query results.

    Args:
        query: SQLAlchemy query object
        page: Page number (1-based)
        per_page: Items per page

    Returns:
        dict: Pagination result with items and metadata
    """
    paginated = query.paginate(page=page, per_page=per_page, error_out=False)

    return {
        "items": [
            item.to_dict() if hasattr(item, "to_dict") else item
            for item in paginated.items
        ],
        "page": page,
        "per_page": per_page,
        "total": paginated.total,
        "pages": paginated.pages,
        "has_next": paginated.has_next,
        "has_prev": paginated.has_prev,
        "next_page": paginated.next_num if paginated.has_next else None,
        "prev_page": paginated.prev_num if paginated.has_prev else None,
    }


def create_error_response(message: str, status_code: int = 400, details: Dict = None):
    """
    Create standardized error response.

    Args:
        message: Error message
        status_code: HTTP status code
        details: Additional error details

    Returns:
        tuple: (response, status_code)
    """
    error_response = {
        "error": message,
        "timestamp": datetime.utcnow().isoformat(),
        "status_code": status_code,
    }

    if details:
        error_response["details"] = details

    return jsonify(error_response), status_code


def create_success_response(
    data: Any, message: str = "Success", status_code: int = 200
):
    """
    Create standardized success response.

    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code

    Returns:
        tuple: (response, status_code)
    """
    if isinstance(data, list):
        response = {
            "message": message,
            "data": data,
            "count": len(data),
            "timestamp": datetime.utcnow().isoformat(),
        }
    else:
        response = {
            "message": message,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }

    return jsonify(response), status_code


def calculate_service_cost(
    base_cost: float,
    parts_cost: float = 0.0,
    labor_hours: float = 1.0,
    labor_rate: float = 75.0,
):
    """
    Calculate total service cost including parts and labor.

    Args:
        base_cost: Base service cost
        parts_cost: Cost of parts used
        labor_hours: Hours of labor
        labor_rate: Labor rate per hour

    Returns:
        dict: Cost breakdown
    """
    labor_cost = labor_hours * labor_rate
    subtotal = base_cost + parts_cost + labor_cost
    tax_rate = 0.08  # 8% tax
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount

    return {
        "base_cost": round(base_cost, 2),
        "parts_cost": round(parts_cost, 2),
        "labor_cost": round(labor_cost, 2),
        "labor_hours": labor_hours,
        "labor_rate": labor_rate,
        "subtotal": round(subtotal, 2),
        "tax_rate": tax_rate,
        "tax_amount": round(tax_amount, 2),
        "total": round(total, 2),
    }


def generate_service_ticket_number() -> str:
    """
    Generate a unique service ticket number.

    Returns:
        str: Service ticket number in format ST-YYYYMMDD-XXXX
    """
    date_part = datetime.now().strftime("%Y%m%d")
    random_part = str(random.randint(1000, 9999))  # nosec B311
    return f"ST-{date_part}-{random_part}"


def is_business_hours() -> bool:
    """
    Check if current time is within business hours (8 AM - 6 PM, Mon-Fri).

    Returns:
        bool: True if within business hours
    """
    now = datetime.now()

    # Check if it's a weekday (0 = Monday, 6 = Sunday)
    if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False

    # Check if it's between 8 AM and 6 PM
    business_start = 8
    business_end = 18

    return business_start <= now.hour < business_end
