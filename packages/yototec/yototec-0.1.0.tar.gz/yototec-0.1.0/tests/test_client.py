"""
Tests Client.
"""

import unittest
from yototec.client import Client


class TestClient(unittest.TestCase):
    """
    Tests Client
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Create a single Client instance for all tests.
        """
        # Replace "YOUR_API_KEY" with a valid API key for testnet or use environment variables
        cls.api_key = "YOUR_API_KEY"  # type: ignore
        cls.client_user = Client(api_key=cls.api_key)  # type: ignore

    def test_01_get_data(self) -> None:
        """
        Get a time series of aggregated price data.
        """
        data = self.client_user.get_data(tic="ETHUSD", sdate="2025-01-01T00:00:00", edate="2025-01-01T01:00:00", freq="minute")  # type: ignore
        self.assertIsNone(
            data, "You may replace YOUR_API_KEY with a valid API key for tests."
        )

    def test_02_get_data_last(self) -> None:
        """
        Get the latest available aggregated price data.
        """
        data = self.client_user.get_data_last(tic="ETHUSD", freq="minute")  # type: ignore
        self.assertIsNone(
            data, "You may replace YOUR_API_KEY with a valid API key for tests."
        )


if __name__ == "__main__":
    unittest.main()
