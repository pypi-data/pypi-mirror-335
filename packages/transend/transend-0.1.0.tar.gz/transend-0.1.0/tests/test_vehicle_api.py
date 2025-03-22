import unittest
from unittest.mock import patch, MagicMock
import pytest
from src.client import VehicleAPI


class TestVehicleAPI(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.api_token = "test_api_token"
        self.base_url = "https://api.test.com"
        self.vehicle_api = VehicleAPI(self.api_key, self.api_token, self.base_url)
        
        # The base_url should be modified to include /vehicle
        self.expected_base_url = f"{self.base_url}/vehicle"

    def test_init(self):
        """Test VehicleAPI initialization."""
        self.assertEqual(self.vehicle_api.api_key, self.api_key)
        self.assertEqual(self.vehicle_api.api_token, self.api_token)
        self.assertEqual(self.vehicle_api.base_url, self.expected_base_url)

    @patch.object(VehicleAPI, '_make_request')
    def test_get_all_dtcs(self, mock_make_request):
        """Test get_all_dtcs method."""
        # Setup mock response
        mock_response = [{"code": "P0123", "description": "Test DTC"}]
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = self.vehicle_api.get_all_dtcs()
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/dtcs")
        self.assertEqual(result, mock_response)

    @patch.object(VehicleAPI, '_make_request')
    def test_get_drive_types_by_vhid(self, mock_make_request):
        """Test get_drive_types_by_vhid method."""
        # Setup mock response
        mock_response = [{"id": 1, "name": "FWD"}]
        mock_make_request.return_value = mock_response
        
        # Test data
        vhid = "123456"
        
        # Call the method
        result = self.vehicle_api.get_drive_types_by_vhid(vhid)
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", f"/drivetype/{vhid}")
        self.assertEqual(result, mock_response)

    @patch.object(VehicleAPI, '_make_request')
    def test_get_engines_by_vhid(self, mock_make_request):
        """Test get_engines_by_vhid method."""
        # Setup mock response
        mock_response = [{"id": 1, "name": "V6 3.5L"}]
        mock_make_request.return_value = mock_response
        
        # Test data
        vhid = "123456"
        
        # Call the method
        result = self.vehicle_api.get_engines_by_vhid(vhid)
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", f"/engine/{vhid}")
        self.assertEqual(result, mock_response)

    @patch.object(VehicleAPI, '_make_request')
    def test_get_makes_by_vhid(self, mock_make_request):
        """Test get_makes_by_vhid method."""
        # Setup mock response
        mock_response = [{"vhid": "234567", "name": "Toyota"}]
        mock_make_request.return_value = mock_response
        
        # Test data
        vhid = "123456"
        
        # Call the method
        result = self.vehicle_api.get_makes_by_vhid(vhid)
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", f"/make/{vhid}")
        self.assertEqual(result, mock_response)

    @patch.object(VehicleAPI, '_make_request')
    def test_get_models_by_vhid(self, mock_make_request):
        """Test get_models_by_vhid method."""
        # Setup mock response
        mock_response = [{"vhid": "345678", "name": "Camry"}]
        mock_make_request.return_value = mock_response
        
        # Test data
        vhid = "234567"
        
        # Call the method
        result = self.vehicle_api.get_models_by_vhid(vhid)
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", f"/model/{vhid}")
        self.assertEqual(result, mock_response)

    @patch.object(VehicleAPI, '_make_request')
    def test_get_transmissions_no_params(self, mock_make_request):
        """Test get_transmissions method with no parameters."""
        # Setup mock response
        mock_response = [{"id": 1, "name": "Automatic"}]
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = self.vehicle_api.get_transmissions()
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/transmission", params={})
        self.assertEqual(result, mock_response)

    @patch.object(VehicleAPI, '_make_request')
    def test_get_transmissions_with_params(self, mock_make_request):
        """Test get_transmissions method with parameters."""
        # Setup mock response
        mock_response = [{"id": 1, "name": "Automatic"}]
        mock_make_request.return_value = mock_response
        
        # Test data
        tag_number = "12345"
        transmission_mfr_code = "ABC"
        
        # Expected params
        expected_params = {
            "tagNumber": tag_number,
            "transmissionMfrCode": transmission_mfr_code
        }
        
        # Call the method
        result = self.vehicle_api.get_transmissions(
            tag_number=tag_number, transmission_mfr_code=transmission_mfr_code
        )
        
        # Assertions
        mock_make_request.assert_called_once_with(
            "GET", "/transmission", params=expected_params
        )
        self.assertEqual(result, mock_response)

    @patch.object(VehicleAPI, '_make_request')
    def test_get_vehicle_by_vhid(self, mock_make_request):
        """Test get_vehicle_by_vhid method."""
        # Setup mock response
        mock_response = [{"id": 1, "year": 2020, "make": "Toyota", "model": "Camry"}]
        mock_make_request.return_value = mock_response
        
        # Test data
        vhid = "123456"
        
        # Call the method
        result = self.vehicle_api.get_vehicle_by_vhid(vhid)
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", f"/{vhid}")
        self.assertEqual(result, mock_response)

    @patch.object(VehicleAPI, '_make_request')
    def test_get_vehicles_by_vin(self, mock_make_request):
        """Test get_vehicles_by_vin method."""
        # Setup mock response
        mock_response = [{"id": 1, "year": 2020, "make": "Toyota", "model": "Camry"}]
        mock_make_request.return_value = mock_response
        
        # Test data
        vin = "1HGBH41JXMN109186"
        
        # Call the method
        result = self.vehicle_api.get_vehicles_by_vin(vin)
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", f"/vin/{vin}")
        self.assertEqual(result, mock_response)

    @patch.object(VehicleAPI, '_make_request')
    def test_get_years_no_vhid(self, mock_make_request):
        """Test get_years method with no vhid."""
        # Setup mock response
        mock_response = [{"vhid": "123", "year": 2020}, {"vhid": "124", "year": 2021}]
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = self.vehicle_api.get_years()
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/years")
        self.assertEqual(result, mock_response)

    @patch.object(VehicleAPI, '_make_request')
    def test_get_years_with_vhid(self, mock_make_request):
        """Test get_years method with vhid."""
        # Setup mock response
        mock_response = [{"vhid": "123", "year": 2020}]
        mock_make_request.return_value = mock_response
        
        # Test data
        vhid = "123"
        
        # Call the method
        result = self.vehicle_api.get_years(vhid=vhid)
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", f"/years/{vhid}")
        self.assertEqual(result, mock_response)

    @patch.object(VehicleAPI, 'get_years')
    @patch.object(VehicleAPI, 'get_makes_by_vhid')
    @patch.object(VehicleAPI, 'get_models_by_vhid')
    def test_get_year_make_model_vhid_success(
        self, mock_get_models, mock_get_makes, mock_get_years
    ):
        """Test get_year_make_model_vhid method with successful flow."""
        # Setup mock responses
        mock_get_years.return_value = [
            {"vhid": "year_123", "year": 2010}
        ]
        mock_get_makes.return_value = [
            {"vhid": "make_123", "name": "Toyota"}
        ]
        mock_get_models.return_value = [
            {"vhid": "model_123", "name": "Camry"}
        ]
        
        # Test data
        year = 2010
        make = "Toyota"
        model = "Camry"
        
        # Call the method
        result = self.vehicle_api.get_year_make_model_vhid(year, make, model)
        
        # Assertions
        mock_get_years.assert_called_once()
        mock_get_makes.assert_called_once_with("year_123")
        mock_get_models.assert_called_once_with("make_123")
        self.assertEqual(result, {"vhid": "model_123"})

    @patch.object(VehicleAPI, 'get_years')
    def test_get_year_make_model_vhid_year_not_found(self, mock_get_years):
        """Test get_year_make_model_vhid method when year is not found."""
        # Setup mock responses
        mock_get_years.return_value = [
            {"vhid": "year_123", "year": 2020}
        ]
        
        # Test data
        year = 2010
        make = "Toyota"
        model = "Camry"
        
        # Call the method
        result = self.vehicle_api.get_year_make_model_vhid(year, make, model)
        
        # Assertions
        mock_get_years.assert_called_once()
        self.assertEqual(result, {"error": "Year not found"})

    @patch.object(VehicleAPI, 'get_years')
    @patch.object(VehicleAPI, 'get_makes_by_vhid')
    def test_get_year_make_model_vhid_make_not_found(
        self, mock_get_makes, mock_get_years
    ):
        """Test get_year_make_model_vhid method when make is not found."""
        # Setup mock responses
        mock_get_years.return_value = [
            {"vhid": "year_123", "year": 2010}
        ]
        mock_get_makes.return_value = [
            {"vhid": "make_123", "name": "Honda"}
        ]
        
        # Test data
        year = 2010
        make = "Toyota"
        model = "Camry"
        
        # Call the method
        result = self.vehicle_api.get_year_make_model_vhid(year, make, model)
        
        # Assertions
        mock_get_years.assert_called_once()
        mock_get_makes.assert_called_once_with("year_123")
        self.assertEqual(result, {"error": "Make not found"})

    @patch.object(VehicleAPI, 'get_years')
    @patch.object(VehicleAPI, 'get_makes_by_vhid')
    @patch.object(VehicleAPI, 'get_models_by_vhid')
    def test_get_year_make_model_vhid_model_not_found(
        self, mock_get_models, mock_get_makes, mock_get_years
    ):
        """Test get_year_make_model_vhid method when model is not found."""
        # Setup mock responses
        mock_get_years.return_value = [
            {"vhid": "year_123", "year": 2010}
        ]
        mock_get_makes.return_value = [
            {"vhid": "make_123", "name": "Toyota"}
        ]
        mock_get_models.return_value = [
            {"vhid": "model_123", "name": "Corolla"}
        ]
        
        # Test data
        year = 2010
        make = "Toyota"
        model = "Camry"
        
        # Call the method
        result = self.vehicle_api.get_year_make_model_vhid(year, make, model)
        
        # Assertions
        mock_get_years.assert_called_once()
        mock_get_makes.assert_called_once_with("year_123")
        mock_get_models.assert_called_once_with("make_123")
        self.assertEqual(result, {"error": "Model not found"})
