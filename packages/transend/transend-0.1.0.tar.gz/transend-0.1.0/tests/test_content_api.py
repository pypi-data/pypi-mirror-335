import unittest
from unittest.mock import patch, MagicMock
import pytest
from src.client import ContentAPI


class TestContentAPI(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_api_key"
        self.api_token = "test_api_token"
        self.base_url = "https://api.test.com"
        self.content_api = ContentAPI(self.api_key, self.api_token, self.base_url)
        
        # The base_url should be modified to include /content
        self.expected_base_url = f"{self.base_url}/content"

    def test_init(self):
        """Test ContentAPI initialization."""
        self.assertEqual(self.content_api.api_key, self.api_key)
        self.assertEqual(self.content_api.api_token, self.api_token)
        self.assertEqual(self.content_api.base_url, self.expected_base_url)

    @patch.object(ContentAPI, '_make_request')
    def test_get_article_resources(self, mock_make_request):
        """Test get_article_resources method."""
        # Setup mock response
        mock_response = [
            {"id": 1, "type": "image", "url": "https://example.com/image1.jpg"},
            {"id": 2, "type": "pdf", "url": "https://example.com/document.pdf"}
        ]
        mock_make_request.return_value = mock_response
        
        # Test data
        article_id = 123
        
        # Call the method
        result = self.content_api.get_article_resources(article_id)
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", f"/article/{article_id}/resource")
        self.assertEqual(result, mock_response)

    @patch.object(ContentAPI, '_make_request')
    def test_get_articles(self, mock_make_request):
        """Test get_articles method."""
        # Setup mock response
        mock_response = [
            {
                "id": 1, 
                "title": "Article 1", 
                "content": "Content of article 1",
                "publishDate": "2023-01-01"
            },
            {
                "id": 2, 
                "title": "Article 2", 
                "content": "Content of article 2",
                "publishDate": "2023-01-02"
            }
        ]
        mock_make_request.return_value = mock_response
        
        # Call the method
        result = self.content_api.get_articles()
        
        # Assertions
        mock_make_request.assert_called_once_with("GET", "/article")
        self.assertEqual(result, mock_response)
