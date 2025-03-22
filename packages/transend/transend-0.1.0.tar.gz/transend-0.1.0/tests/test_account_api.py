import unittest
from unittest.mock import patch, MagicMock
import pytest
from uuid import UUID
from src.client import AccountAPI


class TestAccountAPI(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.api_token = "test_api_token"
        self.base_url = "https://api.test.com"
        self.account_api = AccountAPI(self.api_key, self.api_token, self.base_url)
        
        # The base_url should be modified to include /account
        self.expected_base_url = f"{self.base_url}/account"

    def test_init(self):
        """Test AccountAPI initialization."""
        self.assertEqual(self.account_api.api_key, self.api_key)
        self.assertEqual(self.account_api.api_token, self.api_token)
        self.assertEqual(self.account_api.base_url, self.expected_base_url)

    @patch.object(AccountAPI, '_make_request')
    def test_delete_bank_account(self, mock_make_request):
        """Test delete_bank_account method."""
        # Setup mock response
        mock_make_request.return_value = None
        
        # Test data
        customer_stripe_id = 12345
        
        # Call the method
        self.account_api.delete_bank_account(customer_stripe_id)
        
        # Assertions
        mock_make_request.assert_called_once_with(
            "DELETE", f"/bank-account/{customer_stripe_id}"
        )

    @patch.object(AccountAPI, '_make_request')
    def test_update_credit_card_default(self, mock_make_request):
        """Test update_credit_card_default method."""
        # Setup mock response
        mock_make_request.return_value = None
        
        # Test data
        credit_card_guid = UUID('a8098c1a-f86e-11da-bd1a-00112444be1e')
        
        # Call the method
        self.account_api.update_credit_card_default(credit_card_guid)
        
        # Assertions
        mock_make_request.assert_called_once_with(
            "PUT", f"/credit-card/{credit_card_guid}"
        )

    @patch.object(AccountAPI, '_make_request')
    def test_delete_credit_card(self, mock_make_request):
        """Test delete_credit_card method."""
        # Setup mock response
        mock_make_request.return_value = None
        
        # Test data
        credit_card_guid = UUID('a8098c1a-f86e-11da-bd1a-00112444be1e')
        
        # Call the method
        self.account_api.delete_credit_card(credit_card_guid)
        
        # Assertions
        mock_make_request.assert_called_once_with(
            "DELETE", f"/credit-card/{credit_card_guid}"
        )

    @patch.object(AccountAPI, '_make_request')
    def test_get_active_bank_accounts(self, mock_make_request):
        """Test get_active_bank_accounts method."""
        # Setup mock response
        mock_response = [
            {"id": 1, "accountNumber": "xxxx1234", "status": "active"},
            {"id": 2, "accountNumber": "xxxx5678", "status": "active"}
        ]
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = self.account_api.get_active_bank_accounts()
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/bank-account/active")
        self.assertEqual(result, mock_response)

    @patch.object(AccountAPI, '_make_request')
    def test_get_credit_cards(self, mock_make_request):
        """Test get_credit_cards method."""
        # Setup mock response
        mock_response = [
            {"id": 1, "cardNumber": "xxxx1234", "expiryDate": "12/25"},
            {"id": 2, "cardNumber": "xxxx5678", "expiryDate": "03/24"}
        ]
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = self.account_api.get_credit_cards()
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/credit-card")
        self.assertEqual(result, mock_response)

    @patch.object(AccountAPI, '_make_request')
    def test_post_credit_card(self, mock_make_request):
        """Test post_credit_card method."""
        # Setup mock response
        mock_response = UUID('a8098c1a-f86e-11da-bd1a-00112444be1e')
        mock_make_request.return_value = mock_response
        
        # Test data
        card_data = {
            "cardNumber": "4111111111111111",
            "expiryDate": "12/25",
            "cvv": "123",
            "name": "John Doe"
        }
        
        # Call the method
        result = self.account_api.post_credit_card(card_data)
        
        # Assertions
        mock_make_request.assert_called_once_with("POST", "/credit-card", data=card_data)
        self.assertEqual(result, mock_response)

    @patch.object(AccountAPI, '_make_request')
    def test_get_customer_info(self, mock_make_request):
        """Test get_customer_info method."""
        # Setup mock response
        mock_response = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "status": "active"
        }
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = self.account_api.get_customer_info()
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/customer/current")
        self.assertEqual(result, mock_response)

    @patch.object(AccountAPI, '_make_request')
    def test_get_verified_bank_accounts(self, mock_make_request):
        """Test get_verified_bank_accounts method."""
        # Setup mock response
        mock_response = [
            {"id": 1, "accountNumber": "xxxx1234", "status": "verified"},
            {"id": 2, "accountNumber": "xxxx5678", "status": "verified"}
        ]
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = self.account_api.get_verified_bank_accounts()
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/bank-account/verified")
        self.assertEqual(result, mock_response)

    @patch.object(AccountAPI, '_make_request')
    def test_post_bank_account(self, mock_make_request):
        """Test post_bank_account method."""
        # Setup mock response
        mock_response = UUID('a8098c1a-f86e-11da-bd1a-00112444be1e')
        mock_make_request.return_value = mock_response
        
        # Test data
        bank_account_data = {
            "accountNumber": "1234567890",
            "routingNumber": "987654321",
            "accountType": "checking",
            "name": "John Doe"
        }
        
        # Call the method
        result = self.account_api.post_bank_account(bank_account_data)
        
        # Assertions
        mock_make_request.assert_called_once_with("POST", "/bank-account", data=bank_account_data)
        self.assertEqual(result, mock_response)

    @patch.object(AccountAPI, '_make_request')
    def test_verify_bank_account(self, mock_make_request):
        """Test verify_bank_account method."""
        # Setup mock response
        mock_response = {
            "status": "verified",
            "message": "Bank account verified successfully"
        }
        mock_make_request.return_value = mock_response
        
        # Test data
        verification_data = {
            "accountId": "1234",
            "amounts": [0.32, 0.45]
        }
        
        # Call the method
        result = self.account_api.verify_bank_account(verification_data)
        
        # Assertions
        mock_make_request.assert_called_once_with("PUT", "/bank-account/verify", data=verification_data)
        self.assertEqual(result, mock_response)
