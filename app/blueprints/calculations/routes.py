from flask import request, jsonify
from . import calculations_bp
from datetime import datetime, timezone


@calculations_bp.route("/add", methods=["POST"])
def add_numbers():
    """Add two or more numbers"""
    try:
        data = request.get_json()

        if not data or "numbers" not in data:
            return jsonify({"error": 'Missing required field "numbers"'}), 400

        numbers = data["numbers"]

        if not isinstance(numbers, list) or len(numbers) < 2:
            return (
                jsonify(
                    {
                        "error": 'Field "numbers" must be an array with at least 2 numbers'
                    }
                ),
                400,
            )

        # Validate each number
        for i, num in enumerate(numbers):
            if not isinstance(num, (int, float)):
                return (
                    jsonify({"error": f"Number at index {i} must be a valid number"}),
                    400,
                )

        result = sum(numbers)

        return (
            jsonify(
                {
                    "operation": "addition",
                    "operands": numbers,
                    "result": result,
                    "calculation": " + ".join(map(str, numbers)) + f" = {result}",
                    "timestamp": datetime.now(timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@calculations_bp.route("/subtract", methods=["POST"])
def subtract_numbers():
    """Subtract numbers (first - second - third...)"""
    try:
        data = request.get_json()

        if not data or "numbers" not in data:
            return jsonify({"error": 'Missing required field "numbers"'}), 400

        numbers = data["numbers"]

        if not isinstance(numbers, list) or len(numbers) < 2:
            return (
                jsonify(
                    {
                        "error": 'Field "numbers" must be an array with at least 2 numbers'
                    }
                ),
                400,
            )

        # Validate each number
        for i, num in enumerate(numbers):
            if not isinstance(num, (int, float)):
                return (
                    jsonify({"error": f"Number at index {i} must be a valid number"}),
                    400,
                )

        result = numbers[0]
        for num in numbers[1:]:
            result -= num

        calc_string = str(numbers[0])
        for num in numbers[1:]:
            calc_string += f" - {num}"
        calc_string += f" = {result}"

        return (
            jsonify(
                {
                    "operation": "subtraction",
                    "operands": numbers,
                    "result": result,
                    "calculation": calc_string,
                    "timestamp": datetime.now(timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@calculations_bp.route("/multiply", methods=["POST"])
def multiply_numbers():
    """Multiply two or more numbers"""
    try:
        data = request.get_json()

        if not data or "numbers" not in data:
            return jsonify({"error": 'Missing required field "numbers"'}), 400

        numbers = data["numbers"]

        if not isinstance(numbers, list) or len(numbers) < 2:
            return (
                jsonify(
                    {
                        "error": 'Field "numbers" must be an array with at least 2 numbers'
                    }
                ),
                400,
            )

        # Validate each number
        for i, num in enumerate(numbers):
            if not isinstance(num, (int, float)):
                return (
                    jsonify({"error": f"Number at index {i} must be a valid number"}),
                    400,
                )

        result = 1
        for num in numbers:
            result *= num

        return (
            jsonify(
                {
                    "operation": "multiplication",
                    "operands": numbers,
                    "result": result,
                    "calculation": " × ".join(map(str, numbers)) + f" = {result}",
                    "timestamp": datetime.now(timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@calculations_bp.route("/divide", methods=["POST"])
def divide_numbers():
    """Divide numbers (first ÷ second ÷ third...)"""
    try:
        data = request.get_json()

        if not data or "numbers" not in data:
            return jsonify({"error": 'Missing required field "numbers"'}), 400

        numbers = data["numbers"]

        if not isinstance(numbers, list) or len(numbers) < 2:
            return (
                jsonify(
                    {
                        "error": 'Field "numbers" must be an array with at least 2 numbers'
                    }
                ),
                400,
            )

        # Validate each number
        for i, num in enumerate(numbers):
            if not isinstance(num, (int, float)):
                return (
                    jsonify({"error": f"Number at index {i} must be a valid number"}),
                    400,
                )

        # Check for division by zero
        for i, num in enumerate(numbers[1:], 1):
            if num == 0:
                return jsonify({"error": f"Division by zero at index {i}"}), 400

        result = numbers[0]
        for num in numbers[1:]:
            result /= num

        calc_string = str(numbers[0])
        for num in numbers[1:]:
            calc_string += f" ÷ {num}"
        calc_string += f" = {result}"

        return (
            jsonify(
                {
                    "operation": "division",
                    "operands": numbers,
                    "result": result,
                    "calculation": calc_string,
                    "timestamp": datetime.now(timezone.utc)
                    .isoformat()
                    .replace("+00:00", "Z"),
                }
            ),
            200,
        )

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@calculations_bp.route("/health", methods=["GET"])
def calculations_health():
    """Health check for calculations service"""
    return (
        jsonify(
            {
                "service": "calculations",
                "status": "healthy",
                "endpoints": [
                    "POST /calculations/add",
                    "POST /calculations/subtract",
                    "POST /calculations/multiply",
                    "POST /calculations/divide",
                ],
            }
        ),
        200,
    )
