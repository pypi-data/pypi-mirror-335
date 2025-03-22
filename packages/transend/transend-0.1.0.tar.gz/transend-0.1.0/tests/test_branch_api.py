import unittest
from unittest.mock import patch, MagicMock
import pytest
from src.client import BranchAPI


class TestBranchAPI(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.api_token = "test_api_token"
        self.base_url = "https://api.test.com"
        self.branch_api = BranchAPI(self.api_key, self.api_token, self.base_url)
        
        # The base_url should be modified to include /branch
        self.expected_base_url = f"{self.base_url}/branch"

    def test_init(self):
        """Test BranchAPI initialization."""
        self.assertEqual(self.branch_api.api_key, self.api_key)
        self.assertEqual(self.branch_api.api_token, self.api_token)
        self.assertEqual(self.branch_api.base_url, self.expected_base_url)

    @patch.object(BranchAPI, '_make_request')
    def test_get_all_branches_no_params(self, mock_make_request):
        """Test get_all_branches method with no parameters."""
        # Setup mock response
        mock_response = [
            {"id": 1, "branchNumber": "101", "name": "Branch 1", "active": True},
            {"id": 2, "branchNumber": "102", "name": "Branch 2", "active": True}
        ]
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = self.branch_api.get_all_branches()
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/", params=None)
        self.assertEqual(result, mock_response)

    @patch.object(BranchAPI, '_make_request')
    def test_get_all_branches_with_active_param(self, mock_make_request):
        """Test get_all_branches method with active parameter."""
        # Setup mock response
        mock_response = [
            {"id": 1, "branchNumber": "101", "name": "Branch 1", "active": True}
        ]
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = self.branch_api.get_all_branches(active=True)
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/", params={"active": True})
        self.assertEqual(result, mock_response)

    @patch.object(BranchAPI, '_make_request')
    def test_get_branch_by_number(self, mock_make_request):
        """Test get_branch_by_number method."""
        # Setup mock response
        mock_response = [{"id": 1, "branchNumber": "101", "name": "Branch 1", "active": True}]
        mock_make_request.return_value = mock_response
        
        # Test data
        branch_number = "101"
        
        # Call the method
        result = self.branch_api.get_branch_by_number(branch_number)
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", f"/{branch_number}")
        self.assertEqual(result, mock_response)
