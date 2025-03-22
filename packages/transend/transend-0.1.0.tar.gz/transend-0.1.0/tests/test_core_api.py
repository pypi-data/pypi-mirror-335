import unittest
from unittest.mock import patch, MagicMock
import pytest
from src.client import CoreAPI


class TestCoreAPI(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.api_token = "test_api_token"
        self.base_url = "https://api.test.com"
        self.core_api = CoreAPI(self.api_key, self.api_token, self.base_url)
        
        # The base_url should be modified to include /core
        self.expected_base_url = f"{self.base_url}/core"

    def test_init(self):
        """Test CoreAPI initialization."""
        self.assertEqual(self.core_api.api_key, self.api_key)
        self.assertEqual(self.core_api.api_token, self.api_token)
        self.assertEqual(self.core_api.base_url, self.expected_base_url)

    @patch.object(CoreAPI, '_make_request')
    def test_get_open_cores(self, mock_make_request):
        """Test get_open_cores method."""
        # Setup mock response
        mock_response = [
            {"id": 1, "name": "Core 1", "status": "open", "value": 100.00},
            {"id": 2, "name": "Core 2", "status": "open", "value": 150.00}
        ]
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = self.core_api.get_open_cores()
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/open")
        self.assertEqual(result, mock_response)
