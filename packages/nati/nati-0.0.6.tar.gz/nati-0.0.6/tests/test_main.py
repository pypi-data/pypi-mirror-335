import unittest
from unittest.mock import patch, MagicMock
import os
from nati.main import check_config


class TestMain(unittest.TestCase):

    @patch("nati.main.os.path.exists")
    def test_check_config_file_missing(self, mock_exists):
        """Test when the config file does not exist"""
        mock_exists.return_value = False

        result = check_config()
        self.assertFalse(result)

    @patch("nati.main.os.path.exists")
    @patch("nati.main.load_config")
    def test_check_config_file_exists_and_valid(self, mock_load_config, mock_exists):
        """Test when the config file exists and is valid"""
        mock_exists.return_value = True
        mock_load_config.return_value = MagicMock()  # Simulating successful load

        result = check_config()
        self.assertTrue(result)

    @patch("nati.main.os.path.exists")
    @patch("nati.main.load_config")
    def test_check_config_file_exists_but_invalid(self, mock_load_config, mock_exists):
        """Test when the config file exists but fails validation"""
        mock_exists.return_value = True
        mock_load_config.side_effect = Exception("Invalid format")

        result = check_config()
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
