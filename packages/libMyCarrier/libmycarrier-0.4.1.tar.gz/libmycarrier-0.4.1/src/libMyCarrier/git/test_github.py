import unittest
from unittest.mock import patch, MagicMock
import json
import sys
import os
import time
import base64
from cryptography.hazmat.primitives.asymmetric import rsa

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from libMyCarrier.git.github import githubAuth


class TestGitHubAuth(unittest.TestCase):
    
    def setUp(self):
        # Generate a private key for testing
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        # Mock the load_pem_private_key function to return our test key
        patcher = patch('libMyCarrier.git.github.load_pem_private_key')
        self.mock_load_key = patcher.start()
        self.mock_load_key.return_value = self.private_key
        self.addCleanup(patcher.stop)
        
        # Mock requests
        requests_patcher = patch('libMyCarrier.git.github.requests')
        self.mock_requests = requests_patcher.start()
        self.addCleanup(requests_patcher.stop)
        
        # Mock response with a token
        mock_response = MagicMock()
        mock_response.content = json.dumps({"token": "test_token"}).encode('utf-8')
        mock_response.raise_for_status = MagicMock()
        self.mock_requests.post.return_value = mock_response

    def test_base64url_encode(self):
        """Test the _base64url_encode method"""
        auth = githubAuth("test_pem", "test_app_id", "test_installation_id")
        
        # Test string input
        result = auth._base64url_encode("test-data")
        self.assertEqual(result, "dGVzdC1kYXRh")
        
        # Test bytes input
        result = auth._base64url_encode(b"test-data")
        self.assertEqual(result, "dGVzdC1kYXRh")
        
        # Test padding removal
        # "test" base64-encoded is "dGVzdA==" with padding
        result = auth._base64url_encode("test")
        self.assertEqual(result, "dGVzdA")  # No padding
    
    @patch('libMyCarrier.git.github.time')
    def test_generate_jwt(self, mock_time):
        """Test the _generate_jwt method"""
        # Mock time to get consistent JWT token
        mock_time.time.return_value = 1600000000
        
        auth = githubAuth("test_pem", "test_app_id", "test_installation_id")
        
        # Patch the sign method to avoid actual signing
        with patch.object(self.private_key, 'sign', return_value=b'test_signature'):
            jwt = auth._generate_jwt()
            
            # Check JWT format (three parts separated by dots)
            parts = jwt.split('.')
            self.assertEqual(len(parts), 3)
            
            # Decode the header and check it
            header_bytes = base64.urlsafe_b64decode(parts[0] + "==")
            header = json.loads(header_bytes.decode('utf-8'))
            self.assertEqual(header, {"alg": "RS256", "typ": "JWT"})
            
            # Decode the payload and check it
            payload_bytes = base64.urlsafe_b64decode(parts[1] + "==")
            payload = json.loads(payload_bytes.decode('utf-8'))
            self.assertEqual(payload["iat"], 1600000000)
            self.assertEqual(payload["exp"], 1600000600)  # iat + 600
            self.assertEqual(payload["iss"], "test_app_id")

    def test_get_auth_token(self):
        """Test the get_auth_token method"""
        # Mock _generate_jwt to return a fixed JWT
        with patch.object(githubAuth, '_generate_jwt', return_value='test.jwt.token'):
            auth = githubAuth("test_pem", "test_app_id", "test_installation_id")
            
            # Check that the token was set correctly
            self.assertEqual(auth.token, "test_token")
            
            # Check that the correct API call was made
            self.mock_requests.post.assert_called_once()
            url = self.mock_requests.post.call_args[0][0]
            headers = self.mock_requests.post.call_args[1]['headers']
            
            self.assertEqual(url, "https://api.github.com/app/installations/test_installation_id/access_tokens")
            self.assertEqual(headers["Authorization"], "Bearer test.jwt.token")
            self.assertEqual(headers["Accept"], "application/vnd.github+json")
            self.assertEqual(headers["X-GitHub-Api-Version"], "2022-11-28")

    def test_get_auth_token_request_exception(self):
        """Test error handling for request exceptions"""
        # Make requests.post raise an exception
        self.mock_requests.post.side_effect = Exception("API error")
        
        with self.assertRaises(RuntimeError) as context:
            githubAuth("test_pem", "test_app_id", "test_installation_id")
            
        self.assertIn("GitHub API request failed", str(context.exception))

    def test_get_auth_token_json_exception(self):
        """Test error handling for JSON parsing exceptions"""
        # Make response.content be invalid JSON
        mock_response = MagicMock()
        mock_response.content = b"Not valid JSON"
        mock_response.raise_for_status = MagicMock()
        self.mock_requests.post.return_value = mock_response
        
        with self.assertRaises(RuntimeError) as context:
            githubAuth("test_pem", "test_app_id", "test_installation_id")
            
        self.assertIn("Failed to parse GitHub response", str(context.exception))


if __name__ == '__main__':
    unittest.main()
