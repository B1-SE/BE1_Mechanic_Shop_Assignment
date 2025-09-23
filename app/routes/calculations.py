"""
Calculations routes for the mechanic shop application.
"""

from flask import Blueprint, request, jsonify
from app.extensions import limiter

# Create calculations blueprint
calculations_bp = Blueprint("calculations", __name__, url_prefix="/calculations")


@calculations_bp.route("/add", methods=["POST"])
@limiter.limit("100 per minute")
def add_numbers():
    """Add a list of numbers"""
    try:
        data = request.get_json()

        # Validate input
        if not data or "numbers" not in data:
            return jsonify({"error": "Missing numbers field"}), 400

        numbers = data["numbers"]

        # Validate numbers list
        if not isinstance(numbers, list):
            return jsonify({"error": "Numbers must be a list"}), 400

        if len(numbers) < 2:
            return jsonify({"error": "At least 2 numbers required"}), 400

        # Validate all items are numbers
        for num in numbers:
            if not isinstance(num, (int, float)):
                return jsonify({"error": "All items must be numbers"}), 400

        # Calculate sum
        result = sum(numbers)

        return (
            jsonify(
                {
                    "result": result,
                    "operation": "addition",
                    "operands": numbers,  # Changed from 'numbers' to 'operands'
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calculations_bp.route("/subtract", methods=["POST"])
@limiter.limit("100 per minute")
def subtract_numbers():
    """Subtract a list of numbers (first - second - third - ...)"""
    try:
        data = request.get_json()

        # Validate input
        if not data or "numbers" not in data:
            return jsonify({"error": "Missing numbers field"}), 400

        numbers = data["numbers"]

        # Validate numbers list
        if not isinstance(numbers, list):
            return jsonify({"error": "Numbers must be a list"}), 400

        if len(numbers) < 2:
            return jsonify({"error": "At least 2 numbers required"}), 400

        # Validate all items are numbers
        for num in numbers:
            if not isinstance(num, (int, float)):
                return jsonify({"error": "All items must be numbers"}), 400

        # Calculate difference (first - rest)
        result = numbers[0]
        for num in numbers[1:]:
            result -= num

        return (
            jsonify(
                {
                    "result": result,
                    "operation": "subtraction",
                    "operands": numbers,  # Changed from 'numbers' to 'operands'
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calculations_bp.route("/multiply", methods=["POST"])
@limiter.limit("100 per minute")
def multiply_numbers():
    """Multiply a list of numbers"""
    try:
        data = request.get_json()

        # Validate input
        if not data or "numbers" not in data:
            return jsonify({"error": "Missing numbers field"}), 400

        numbers = data["numbers"]

        # Validate numbers list
        if not isinstance(numbers, list):
            return jsonify({"error": "Numbers must be a list"}), 400

        if len(numbers) < 2:
            return jsonify({"error": "At least 2 numbers required"}), 400

        # Validate all items are numbers
        for num in numbers:
            if not isinstance(num, (int, float)):
                return jsonify({"error": "All items must be numbers"}), 400

        # Calculate product
        result = 1
        for num in numbers:
            result *= num

        return (
            jsonify(
                {
                    "result": result,
                    "operation": "multiplication",
                    "operands": numbers,  # Changed from 'numbers' to 'operands'
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calculations_bp.route("/divide", methods=["POST"])
@limiter.limit("100 per minute")
def divide_numbers():
    """Divide a list of numbers (first / second / third / ...)"""
    try:
        data = request.get_json()

        # Validate input
        if not data or "numbers" not in data:
            return jsonify({"error": "Missing numbers field"}), 400

        numbers = data["numbers"]

        # Validate numbers list
        if not isinstance(numbers, list):
            return jsonify({"error": "Numbers must be a list"}), 400

        if len(numbers) < 2:
            return jsonify({"error": "At least 2 numbers required"}), 400

        # Validate all items are numbers
        for num in numbers:
            if not isinstance(num, (int, float)):
                return jsonify({"error": "All items must be numbers"}), 400

        # Check for division by zero
        for num in numbers[1:]:
            if num == 0:
                return jsonify({"error": "Division by zero"}), 400

        # Calculate division (first / rest)
        result = numbers[0]
        for num in numbers[1:]:
            result /= num

        return (
            jsonify(
                {
                    "result": result,
                    "operation": "division",
                    "operands": numbers,  # Changed from 'numbers' to 'operands'
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calculations_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for calculations service"""
    return (
        jsonify(
            {
                "status": "healthy",
                "service": "calculations",
                "endpoints": [
                    "/add",
                    "/subtract",
                    "/multiply",
                    "/divide",
                ],  # Added this field
                "available_operations": ["add", "subtract", "multiply", "divide"],
            }
        ),
        200,
    )
