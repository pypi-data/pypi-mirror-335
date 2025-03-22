"""
HTTP client for interacting with the Kradle API.
"""

import os
from typing import Optional, Dict

from .http import HTTPClient
from .resources import AgentAPI, RunAPI, LogAPI


DEFAULT_BASE_URL = "https://api.kradle.ai/v0"


class KradleAPI:
    """Client for making HTTP requests to the Kradle API."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        """Initialize the API client.

        Args:
            api_key: Optional API key for authentication. If not provided, will check KRADLE_API_KEY env var
            base_url: Optional base URL for the API. If not provided, will check KRADLE_API_URL env var
                     or fall back to default
        """
        self.api_key = api_key or os.getenv("KRADLE_API_KEY")
        self.base_url = base_url or os.getenv("KRADLE_API_URL") or DEFAULT_BASE_URL

        self._init_client()

    def _init_client(self):
        """
        Initialize the HTTP client and API resources on this class
        """
        # Ensure base URL ends with /
        if not self.base_url.endswith("/"):
            self.base_url += "/"

        if self.base_url != DEFAULT_BASE_URL:
            print(f"Using custom base URL: {self.base_url}")

        # Initialize HTTP client
        self.http = HTTPClient(self.base_url, self._get_headers)

        # Initialize API resources
        self.agents = AgentAPI(self.http)
        self.runs = RunAPI(self.http)
        self.logs = LogAPI(self.http)

    def _reload_env(self):
        """
        If there's no API key already, attempt to reload the environment variables

        This is needed if they were set late (for example with load_dotenv())
        """
        if not self.api_key:
            self.api_key = os.getenv("KRADLE_API_KEY")
            self.base_url = os.getenv("KRADLE_API_URL") or DEFAULT_BASE_URL

            # we need to reinitialize the client since the base url has changed
            self._init_client()

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""

        self._reload_env()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def set_api_key(self, api_key: str):
        """Update the API key for the API client."""
        self.api_key = api_key
        # No need to _init_client since the base url hasn't changed

    def validate_api_key(self):
        """Validate the Client has an API key set."""
        self._reload_env()
        if not self.api_key:
            raise Exception("No API key found")
