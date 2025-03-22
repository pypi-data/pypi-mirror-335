import unittest
from unittest.mock import patch, MagicMock
import pytest
from src.client import CustomerAPI


class TestCustomerAPI(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.api_token = "test_api_token"
        self.base_url = "https://api.test.com"
        self.customer_api = CustomerAPI(self.api_key, self.api_token, self.base_url)
        
        # The base_url should be modified to include /customer
        self.expected_base_url = f"{self.base_url}/customer"

    def test_init(self):
        """Test CustomerAPI initialization."""
        self.assertEqual(self.customer_api.api_key, self.api_key)
        self.assertEqual(self.customer_api.api_token, self.api_token)
        self.assertEqual(self.customer_api.base_url, self.expected_base_url)

    @patch.object(CustomerAPI, '_make_request')
    def test_get_users(self, mock_make_request):
        """Test get_users method."""
        # Setup mock response
        mock_response = [
            {"id": 1, "name": "John Doe", "email": "john@example.com", "role": "admin"},
            {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "role": "user"}
        ]
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = self.customer_api.get_users()
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/user")
        self.assertEqual(result, mock_response)
