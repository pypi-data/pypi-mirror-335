import unittest
from unittest.mock import patch
import datetime

from nati.utils import today  # Import the function from utils.py

class TestUtils(unittest.TestCase):
    @patch("nati.utils.datetime.date")  # Patch datetime.date instead of datetime.datetime
    def test_today(self, mock_date):
        """Test today() function returns expected ISO date."""
        mock_date.today.return_value = datetime.date(2025, 3, 17)
        mock_date.isoformat.return_value = "2025-03-17"  # Ensure isoformat() behaves correctly

        self.assertEqual(today(), "2025-03-17")

if __name__ == "__main__":
    unittest.main()
