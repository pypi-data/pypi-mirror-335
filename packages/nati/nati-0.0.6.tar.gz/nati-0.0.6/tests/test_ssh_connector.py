import unittest
from unittest.mock import patch, MagicMock
from nati.ssh_connector import get_device_info  # Ensure correct import

class TestSSHConnector(unittest.TestCase):

    @patch("nati.ssh_connector.ConnectHandler")  # Patch with full module path
    def test_get_device_info_success(self, mock_connect_handler):
        mock_conn = MagicMock()
        mock_conn.send_command.side_effect = [
            "hostname Router1\n",
            "Version 15.2\n"
        ]
        mock_connect_handler.return_value.__enter__.return_value = mock_conn

        result = get_device_info("192.168.1.1", "admin", "password")

        self.assertEqual(result, {"hostname": "hostname Router1", "version": "Version 15.2"})

    @patch("nati.ssh_connector.ConnectHandler")
    def test_get_device_info_connection_failure(self, mock_connect_handler):
        mock_connect_handler.side_effect = Exception("Connection timeout")

        result = get_device_info("192.168.1.1", "admin", "password")

        self.assertIn("error", result)
        self.assertEqual(result["error"], "Connection timeout")

if __name__ == "__main__":
    unittest.main()
