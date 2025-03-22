import unittest
from unittest.mock import patch, MagicMock
import pytest
from src.client import BaseAPI


class TestBaseAPI(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.api_token = "test_api_token"
        self.base_url = "https://api.test.com"
        self.base_api = BaseAPI(self.api_key, self.api_token, self.base_url)

    def test_init(self):
        """Test BaseAPI initialization."""
        self.assertEqual(self.base_api.api_key, self.api_key)
        self.assertEqual(self.base_api.api_token, self.api_token)
        self.assertEqual(self.base_api.base_url, self.base_url)
        
        expected_headers = {
            "Authorization": f"Bearer {self.api_token}",
            "x-api-key": self.api_key,
            "Content-Type": "application/json",
        }
        self.assertEqual(self.base_api.headers, expected_headers)

    @patch("requests.request")
    def test_make_request_get(self, mock_request):
        """Test _make_request for GET method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test_data"}
        mock_request.return_value = mock_response
        
        # Call the method
        result = self.base_api._make_request("GET", "/test")
        
        # Assertions
        mock_request.assert_called_once_with(
            "GET", 
            f"{self.base_url}/test", 
            headers=self.base_api.headers, 
            params=None, 
            json=None
        )
        self.assertEqual(result, {"data": "test_data"})

    @patch("requests.request")
    def test_make_request_post(self, mock_request):
        """Test _make_request for POST method."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.json.return_value = {"data": "test_data"}
        mock_request.return_value = mock_response
        
        # Test data
        test_data = {"test_key": "test_value"}
        test_params = {"param1": "value1"}
        
        # Call the method
        result = self.base_api._make_request("POST", "/test", params=test_params, data=test_data)
        
        # Assertions
        mock_request.assert_called_once_with(
            "POST", 
            f"{self.base_url}/test", 
            headers=self.base_api.headers, 
            params=test_params, 
            json=test_data
        )
        self.assertEqual(result, {"data": "test_data"})

    @patch("requests.request")
    def test_make_request_raises_exception(self, mock_request):
        """Test _make_request raises exception on error."""
        # Setup mock response to raise exception
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("API Error")
        mock_request.return_value = mock_response
        
        # Call the method and expect exception
        with self.assertRaises(Exception):
            self.base_api._make_request("GET", "/test")
