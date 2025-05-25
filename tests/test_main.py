import os
os.environ["USE_GCP"] = "false"  # set before importing app

from unittest.mock import patch
import unittest
from src.main import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    @patch("src.main.run_v2.ServicesClient")
    def test_valid_request_simulation(self, mock_services_client):
        message = {
            "message": {
                "data": "dGVzdA=="  # base64 for "test"
            }
        }
        response = self.client.post("/", json=message)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Simulation complete", response.data)

    def test_invalid_request(self):
        response = self.client.post("/", json={})
        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()
