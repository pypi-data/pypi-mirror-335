import logging
from typing import Any, Dict, Optional

import requests
from requests.exceptions import ConnectionError, HTTPError, RequestException, Timeout


class BaseAPIClient:
    """A base class for making GET requests to an API."""

    DEFAULT_TIMEOUT = 10

    def __init__(
        self,
        base_url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = DEFAULT_TIMEOUT,
    ) -> None:
        """
        Initialize the API client.

        Args:
            base_url (str): The base URL for the API.
            headers (Optional[Dict[str, str]]): Optional HTTP headers to include in requests.
            timeout (Optional[int]): Request timeout in seconds.
        """
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.timeout = timeout
        self.logger = logging.getLogger(self.__class__.__name__)

        if headers:
            self.session.headers.update(headers)

    def _get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
        cookies: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """
        Perform a GET request to the given endpoint.

        Args:
            endpoint (str): The API endpoint to call (without the base URL).
            params (Optional[Dict[str, Any]]): Query parameters to include in the request.

        Returns:
            Any: Parsed JSON response.

        Raises:
            HTTPError: If the request fails due to an HTTP error.
            RequestException: For other request-related issues.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = self.session.get(
                url,
                params=params,
                headers=headers,
                timeout=self.timeout,
                cookies=cookies,
            )
            print(response.url)
            response.raise_for_status()
            return response
        except Timeout:
            self.logger.error(f"Request timed out: {url}")
            raise
        except ConnectionError:
            self.logger.error(f"Connection error: {url}")
            raise
        except HTTPError as http_err:
            self.logger.error(http_err)
            raise
        except RequestException as req_err:
            self.logger.error(f"Request failed for {url}: {req_err}")
            raise

    def close(self) -> None:
        """Close the session to free up resources."""
        self.session.close()
        self.logger.info("Session closed.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
        if exc_type:
            self.logger.error(f"Exception occoured {exc_value}")
        return False
