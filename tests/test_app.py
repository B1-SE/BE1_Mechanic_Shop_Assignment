"""
Unit tests for the main application and general endpoints.
"""

import unittest
import json
from app import create_app
from config import config


class AppTestCase(unittest.TestCase):
    """This class represents the application test case."""

    def setUp(self):
        """
        Define test variables and initialize app.
        This method is called before each test.
        """
        self.app = create_app(config_class=config["testing"])
        self.client = self.app.test_client()

        # Propagate the exceptions to the test client
        self.app.testing = True

    def tearDown(self):
        """
        This method is called after each test.
        """
        pass

    def test_health_check_endpoint(self):
        """Test the /health endpoint."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data["status"], "healthy")

    def test_index_endpoint(self):
        """Test the root / endpoint."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertEqual(json_data["message"], "Welcome to the Mechanic Shop API")

    # --- Tests for the /calculations/sum endpoint ---

    def test_sum_endpoint_success(self):
        """
        Test the /calculations/sum endpoint with valid data.
        This follows the GREEN phase of TDD, verifying correct implementation.
        """
        payload = {"numbers": [10, 20, 30.5]}
        response = self.client.post(
            "/calculations/sum",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        json_data = json.loads(response.data)
        self.assertIn("result", json_data)
        self.assertAlmostEqual(json_data["result"], 60.5)

    def test_sum_endpoint_invalid_data(self):
        """
        Test the /calculations/sum endpoint with invalid (non-numeric) data.
        This is a negative test to ensure robust error handling.
        """
        payload = {"numbers": [10, "twenty", 30]}
        response = self.client.post(
            "/calculations/sum",
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        json_data = json.loads(response.data)
        self.assertIn("error", json_data)
        self.assertEqual(json_data["error"], "Invalid input: all items must be numbers.")


if __name__ == "__main__":
    unittest.main()