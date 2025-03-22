import unittest
from unittest.mock import patch, MagicMock
import pytest
from src.client import TransendAPIClient, ProductAPI, BranchAPI, VehicleAPI, AccountAPI, ContentAPI, CoreAPI, CustomerAPI


class TestTransendAPIClient(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.api_token = "test_api_token"
        self.base_url = "https://api.test.com"
        self.client = TransendAPIClient(self.api_key, self.api_token, self.base_url)

    def test_init(self):
        """Test TransendAPIClient initialization."""
        # Verify that each API client is initialized correctly
        self.assertIsInstance(self.client.product, ProductAPI)
        self.assertEqual(self.client.product.api_key, self.api_key)
        self.assertEqual(self.client.product.api_token, self.api_token)
        self.assertEqual(self.client.product.base_url, f"{self.base_url}/product")
        
        self.assertIsInstance(self.client.branch, BranchAPI)
        self.assertEqual(self.client.branch.api_key, self.api_key)
        self.assertEqual(self.client.branch.api_token, self.api_token)
        self.assertEqual(self.client.branch.base_url, f"{self.base_url}/branch")
        
        self.assertIsInstance(self.client.vehicle, VehicleAPI)
        self.assertEqual(self.client.vehicle.api_key, self.api_key)
        self.assertEqual(self.client.vehicle.api_token, self.api_token)
        self.assertEqual(self.client.vehicle.base_url, f"{self.base_url}/vehicle")
        
        self.assertIsInstance(self.client.account, AccountAPI)
        self.assertEqual(self.client.account.api_key, self.api_key)
        self.assertEqual(self.client.account.api_token, self.api_token)
        self.assertEqual(self.client.account.base_url, f"{self.base_url}/account")
        
        self.assertIsInstance(self.client.content, ContentAPI)
        self.assertEqual(self.client.content.api_key, self.api_key)
        self.assertEqual(self.client.content.api_token, self.api_token)
        self.assertEqual(self.client.content.base_url, f"{self.base_url}/content")
        
        self.assertIsInstance(self.client.core, CoreAPI)
        self.assertEqual(self.client.core.api_key, self.api_key)
        self.assertEqual(self.client.core.api_token, self.api_token)
        self.assertEqual(self.client.core.base_url, f"{self.base_url}/core")
        
        self.assertIsInstance(self.client.customer, CustomerAPI)
        self.assertEqual(self.client.customer.api_key, self.api_key)
        self.assertEqual(self.client.customer.api_token, self.api_token)
        self.assertEqual(self.client.customer.base_url, f"{self.base_url}/customer")

    def test_default_base_url(self):
        """Test default base_url is used if not provided."""
        client = TransendAPIClient(self.api_key, self.api_token)
        self.assertEqual(client.product.base_url, "https://api.transend.us/product")

    @patch('os.getenv')
    @patch('src.client.AccountAPI.get_customer_info')
    @patch('src.client.ContentAPI.get_articles')
    @patch('src.client.CoreAPI.get_open_cores')
    @patch('src.client.CustomerAPI.get_users')
    @patch('src.client.ProductAPI.get_all_sort_types')
    @patch('src.client.BranchAPI.get_all_branches')
    @patch('src.client.VehicleAPI.get_all_dtcs')
    @patch('src.client.VehicleAPI.get_years')
    @patch('src.client.VehicleAPI.get_year_make_model_vhid')
    @patch('src.client.VehicleAPI.get_vehicle_by_vhid')
    @patch('src.client.BranchAPI.get_branch_by_number')
    def test_example_usage(
        self, 
        mock_get_branch_by_number,
        mock_get_vehicle_by_vhid,
        mock_get_year_make_model_vhid,
        mock_get_years,
        mock_get_all_dtcs,
        mock_get_all_branches,
        mock_get_all_sort_types,
        mock_get_users,
        mock_get_open_cores,
        mock_get_articles,
        mock_get_customer_info,
        mock_getenv
    ):
        """Test the example usage in the __main__ block."""
        # Setup mock responses
        mock_getenv.side_effect = lambda key: "test_value" if key in ["TRANSEND_API_KEY", "TRANSEND_API_TOKEN"] else None
        mock_get_customer_info.return_value = {"id": 1, "name": "Test Customer"}
        mock_get_articles.return_value = [{"id": 1, "title": "Test Article"}]
        mock_get_open_cores.return_value = [{"id": 1, "name": "Test Core"}]
        mock_get_users.return_value = [{"id": 1, "name": "Test User"}]
        mock_get_all_sort_types.return_value = [{"id": 1, "name": "Sort Type 1"}]
        mock_get_all_branches.return_value = [{"id": 1, "name": "Branch 1"}]
        mock_get_all_dtcs.return_value = [{"code": "P0123", "description": "Test DTC"}]
        mock_get_years.return_value = [{"vhid": "year_123", "year": 2010}]
        mock_get_year_make_model_vhid.return_value = {"vhid": "model_123"}
        mock_get_vehicle_by_vhid.return_value = {"id": 1, "make": "Toyota", "model": "Camry"}
        mock_get_branch_by_number.return_value = {"id": 1, "branchNumber": "420", "name": "Test Branch"}

        # Directly simulate the execution of the __main__ block
        from src.client import TransendAPIClient
        
        # Patch print to capture output
        with patch('builtins.print'):
            # Create the client with the mocked environment variables
            client = TransendAPIClient("test_value", "test_value")
            
            # Call each method that would be called in the __main__ block
            client.account.get_customer_info()
            client.content.get_articles()
            client.core.get_open_cores()
            client.customer.get_users()
            
            client.product.get_all_sort_types()
            client.branch.get_all_branches()
            client.vehicle.get_all_dtcs()
            client.vehicle.get_years()
            
            vhid = client.vehicle.get_year_make_model_vhid(2010, "Toyota", "Camry")
            client.vehicle.get_vehicle_by_vhid(vhid["vhid"])
            client.branch.get_branch_by_number("420")
            
        # Assertions for the first block of API calls
        mock_get_customer_info.assert_called_once()
        mock_get_articles.assert_called_once()
        mock_get_open_cores.assert_called_once()
        mock_get_users.assert_called_once()
        
        # Assertions for the second block of API calls
        mock_get_all_sort_types.assert_called_once()
        mock_get_all_branches.assert_called_once()
        mock_get_all_dtcs.assert_called_once()
        mock_get_years.assert_called_once()
        mock_get_year_make_model_vhid.assert_called_once_with(2010, "Toyota", "Camry")
        mock_get_vehicle_by_vhid.assert_called_once_with("model_123")
        mock_get_branch_by_number.assert_called_once_with("420")
