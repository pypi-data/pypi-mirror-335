"""
A Python Client to interact with the Yototec Market API.
"""

from typing import Dict, Optional
import requests  # type: ignore


BASE_URL = "https://market.yototec.com"


class Client:
    """
    A Python client that wraps interactions with the Yototec Market API.
    """

    def __init__(self, base_url: str = BASE_URL, api_key: str = ""):
        """
        Initialize the client with a base URL and an optional API key.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def get_data(
        self, tic: str, sdate: str, edate: str, freq: str = "minute"
    ) -> Optional[Dict[str, Dict[str, float]]]:
        """
        Return a time series of aggregated prices for a ticker in a user-defined
        `freq` (i.e. "minute", "hour", "day") in range [`sdate`, `edate`],
        where `sdate` and `edate` should follow ISO 8601
        https://www.iso.org/iso-8601-date-and-time-format.html
        A valid query-param `api_key` is required.
        """
        resp = requests.get(
            f"{self.base_url}/data/get_data?tic={tic}&sdate={sdate}&edate={edate}&freq={freq}&api_key={self.api_key}",
        )
        if resp.status_code == 200:
            data: Dict[str, Dict[str, float]] = resp.json()
            return data
        return None

    def get_data_last(
        self, tic: str, freq: str = "minute"
    ) -> Optional[Dict[str, Dict[str, float]]]:
        """
        Return the latest available aggregated price for a ticker in a user-defined
        `freq` (i.e. "minute", "hour", "day").
        A valid query-param `api_key` is required.
        """
        resp = requests.get(
            f"{self.base_url}/data/get_data_last?tic={tic}&freq={freq}&api_key={self.api_key}",
        )
        if resp.status_code == 200:
            data: Dict[str, Dict[str, float]] = resp.json()
            return data
        return None
