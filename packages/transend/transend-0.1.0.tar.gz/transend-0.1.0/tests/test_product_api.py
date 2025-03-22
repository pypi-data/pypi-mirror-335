import unittest
from unittest.mock import patch, MagicMock
import pytest
from src.client import ProductAPI


class TestProductAPI(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.api_token = "test_api_token"
        self.base_url = "https://api.test.com"
        self.product_api = ProductAPI(self.api_key, self.api_token, self.base_url)
        
        # The base_url should be modified to include /product
        self.expected_base_url = f"{self.base_url}/product"

    def test_init(self):
        """Test ProductAPI initialization."""
        self.assertEqual(self.product_api.api_key, self.api_key)
        self.assertEqual(self.product_api.api_token, self.api_token)
        self.assertEqual(self.product_api.base_url, self.expected_base_url)

    @patch.object(ProductAPI, '_make_request')
    def test_get_all_sort_types(self, mock_make_request):
        """Test get_all_sort_types method."""
        # Setup mock response
        mock_response = [{"id": 1, "name": "Sort Type 1"}, {"id": 2, "name": "Sort Type 2"}]
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = self.product_api.get_all_sort_types()
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/sort/type")
        self.assertEqual(result, mock_response)

    @patch.object(ProductAPI, '_make_request')
    def test_get_all_tags(self, mock_make_request):
        """Test get_all_tags method."""
        # Setup mock response
        mock_response = [{"id": 1, "name": "Tag 1"}, {"id": 2, "name": "Tag 2"}]
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = self.product_api.get_all_tags()
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/tag")
        self.assertEqual(result, mock_response)

    @patch.object(ProductAPI, '_make_request')
    def test_get_availability_by_item_id(self, mock_make_request):
        """Test get_availability_by_item_id method."""
        # Setup mock response
        mock_response = [{"branchId": 1, "quantity": 10}, {"branchId": 2, "quantity": 5}]
        mock_make_request.return_value = mock_response
        
        # Test data
        item_id = "123456"
        
        # Call the method
        result = self.product_api.get_availability_by_item_id(item_id)
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", f"/{item_id}/availability")
        self.assertEqual(result, mock_response)

    @patch.object(ProductAPI, '_make_request')
    def test_get_available_quantity(self, mock_make_request):
        """Test get_available_quantity method."""
        # Setup mock response
        mock_response = {"quantity": 10}
        mock_make_request.return_value = mock_response
        
        # Test data
        item_id = "123456"
        branch_number = "420"
        availability_type_id = "1"
        
        # Expected params
        expected_params = {
            "itemId": item_id,
            "branchNumber": branch_number,
            "availabilityTypeId": availability_type_id
        }
        
        # Call the method
        result = self.product_api.get_available_quantity(
            item_id, branch_number, availability_type_id
        )
        
        # Assertions
        mock_make_request.assert_called_once_with(
            "GET", "/quantity/available", params=expected_params
        )
        self.assertEqual(result, mock_response)

    @patch.object(ProductAPI, '_make_request')
    def test_get_brands_no_params(self, mock_make_request):
        """Test get_brands method with no parameters."""
        # Setup mock response
        mock_response = [{"id": 1, "name": "Brand 1"}, {"id": 2, "name": "Brand 2"}]
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = self.product_api.get_brands()
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/brand", params={})
        self.assertEqual(result, mock_response)

    @patch.object(ProductAPI, '_make_request')
    def test_get_brands_with_params(self, mock_make_request):
        """Test get_brands method with parameters."""
        # Setup mock response
        mock_response = [{"id": 1, "name": "Brand 1"}]
        mock_make_request.return_value = mock_response
        
        # Test data
        vhid = "123"
        phid = "456"
        
        # Expected params
        expected_params = {
            "vhid": vhid,
            "phid": phid
        }
        
        # Call the method
        result = self.product_api.get_brands(vhid=vhid, phid=phid)
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/brand", params=expected_params)
        self.assertEqual(result, mock_response)

    @patch.object(ProductAPI, '_make_request')
    def test_get_categories_no_params(self, mock_make_request):
        """Test get_categories method with no parameters."""
        # Setup mock response
        mock_response = [{"id": 1, "name": "Category 1"}, {"id": 2, "name": "Category 2"}]
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = self.product_api.get_categories()
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/category", params={})
        self.assertEqual(result, mock_response)

    @patch.object(ProductAPI, '_make_request')
    def test_get_categories_with_params(self, mock_make_request):
        """Test get_categories method with parameters."""
        # Setup mock response
        mock_response = [{"id": 1, "name": "Category 1"}]
        mock_make_request.return_value = mock_response
        
        # Test data
        vhid = "123"
        phid = "456"
        search_id = "789"
        
        # Expected params
        expected_params = {
            "vhid": vhid,
            "phid": phid,
            "searchId": search_id
        }
        
        # Call the method
        result = self.product_api.get_categories(vhid=vhid, phid=phid, search_id=search_id)
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/category", params=expected_params)
        self.assertEqual(result, mock_response)
