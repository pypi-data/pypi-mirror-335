import unittest
from unittest.mock import patch, MagicMock
from lockana.client import LockanaClient

class TestLockanaClient(unittest.TestCase):

    @patch('lockana.client.LockanaAuth.auth_login')
    def test_auth_login(self, mock_auth_login):
        """Test the login functionality"""
        mock_auth_login.return_value = "mocked_token"
        
        client = LockanaClient("PYTHON_TEST", "http://localhost:8000")
        
        token = client.auth_login("867865")
        
        self.assertEqual(token, "mocked_token")
        self.assertEqual(client.token, "mocked_token")
        mock_auth_login.assert_called_once_with("867865")
    
    @patch('lockana.client.LockanaAuth.auth_logout')
    def test_auth_logout(self, mock_auth_logout):
        """Test the logout functionality"""
        mock_auth_logout.return_value = None
        
        client = LockanaClient("PYTHON_TEST", "http://localhost:8000")
        client.token = "mocked_token"
        
        client.auth_logout()
        
        self.assertIsNone(client.token)
        mock_auth_logout.assert_called_once()

    @patch('lockana.client.LockanaSecrets.secrets_add')
    @patch('lockana.client.LockanaSecrets.secrets_list')
    @patch('lockana.client.LockanaSecrets.secrets_delete')
    def test_secret_operations(self, mock_secrets_delete, mock_secrets_list, mock_secrets_add):
        """Test secret operations: add, list, and delete"""
        
        mock_secrets_add.return_value = None
        mock_secrets_list.return_value = ["TEST_SECRET"]
        mock_secrets_delete.return_value = None
        
        client = LockanaClient("PYTHON_TEST", "http://localhost:8000")
        client.token = "mocked_token"
        
        client.secrets_add("TEST_SECRET", "TEST_SECRET_VALUE")
        mock_secrets_add.assert_called_once_with("TEST_SECRET", "TEST_SECRET_VALUE")
        
        secrets = client.secrets_list()
        self.assertEqual(secrets, ["TEST_SECRET"])
        mock_secrets_list.assert_called_once()
        
        client.secrets_delete("TEST_SECRET")
        mock_secrets_delete.assert_called_once_with("TEST_SECRET")

if __name__ == '__main__':
    unittest.main()
