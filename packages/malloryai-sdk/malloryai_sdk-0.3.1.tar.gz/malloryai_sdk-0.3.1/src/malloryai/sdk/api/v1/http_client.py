import aiohttp
import requests
from typing import Optional, Dict, Any
import logging

from malloryai.sdk.api.v1.exceptions.exception import APIError
from malloryai.sdk.api.v1.exceptions.not_found import NotFoundError
from malloryai.sdk.api.v1.exceptions.validation import ValidationError


class HttpClient:
    """Handles HTTP interactions with the API with enhanced logging."""

    DEFAULT_BASE_URL = "https://api.mallory.ai/v1"

    def __init__(
        self,
        api_key: str,
        base_url: Optional[str] = None,
        logger: Optional[logging.Logger] = None,
    ):
        """
        Initialize the HTTP client with API key, an optional custom base URL, and set up headers.

        :param api_key: Authentication API key for the Mallory API
        :param base_url: Optional custom base URL for the API endpoints.
        """
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        self.logger = logger or logging.getLogger(__name__)
        self.logger.info(
            f"HttpClient initialized with API key (last 4 chars: {api_key[-4:]}) and base_url: {self.base_url}"
        )

    # -----------------------
    # ASYNCHRONOUS METHODS
    # -----------------------

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Perform an async HTTP GET request with optional query parameters.
        """
        full_url = f"{self.base_url}{endpoint}"
        self.logger.info(f"GET request to {full_url}")
        self.logger.debug(f"GET request params: {params}")

        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(full_url, params=params) as response:
                    self.logger.info(f"GET response status: {response.status}")
                    return await self._handle_response(response)
        except aiohttp.ClientError as e:
            self.logger.error(f"Network error during GET request: {e}")
            raise

    async def post(
        self,
        endpoint: str,
        json: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Perform an async HTTP POST request with JSON payload.
        """
        full_url = f"{self.base_url}{endpoint}"
        self.logger.info(f"POST request to {full_url}")
        self.logger.debug(f"POST request payload: {json}")

        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.post(full_url, json=json, params=params) as response:
                    self.logger.info(f"POST response status: {response.status}")
                    return await self._handle_response(response)
        except aiohttp.ClientError as e:
            self.logger.error(f"Network error during POST request: {e}")
            raise

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Any:
        """
        Handle the API response asynchronously.
        """
        try:
            response_text = await response.text()
            self.logger.debug(f"Response body: {response_text}")

            if response.status == 200:
                return await response.json()
            elif response.status == 404:
                self.logger.error(
                    f"Not Found Error - Status: {response.status}, Message: {response_text}"
                )
                raise NotFoundError(response_text)
            elif response.status == 422:
                self.logger.error(
                    f"Validation Error - Status: {response.status}, Message: {response_text}"
                )
                raise ValidationError(response_text)
            else:
                self.logger.error(
                    f"API Error - Status: {response.status}, Message: {response_text}"
                )
                raise APIError(response.status, response_text)
        except Exception as e:
            self.logger.error(f"Error processing response: {e}")
            raise

    # -----------------------
    # SYNCHRONOUS METHODS
    # -----------------------

    def get_sync(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """
        Perform a synchronous HTTP GET request with optional query parameters.
        """
        full_url = f"{self.base_url}{endpoint}"
        self.logger.info(f"GET (sync) request to {full_url}")
        self.logger.debug(f"GET (sync) request params: {params}")

        try:
            response = requests.get(full_url, headers=self.headers, params=params)
            self.logger.info(f"GET (sync) response status: {response.status_code}")
            return self._handle_response_sync(response)
        except requests.RequestException as e:
            self.logger.error(f"Network error during GET (sync) request: {e}")
            raise

    def post_sync(
        self,
        endpoint: str,
        json: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Perform a synchronous HTTP POST request with JSON payload.
        """
        full_url = f"{self.base_url}{endpoint}"
        self.logger.info(f"POST (sync) request to {full_url}")
        self.logger.debug(f"POST (sync) request payload: {json}")

        try:
            response = requests.post(
                full_url, headers=self.headers, json=json, params=params
            )
            self.logger.info(f"POST (sync) response status: {response.status_code}")
            return self._handle_response_sync(response)
        except requests.RequestException as e:
            self.logger.error(f"Network error during POST (sync) request: {e}")
            raise

    def _handle_response_sync(self, response: requests.Response) -> Any:
        """
        Handle the API response synchronously.
        """
        response_text = response.text
        self.logger.debug(f"Response body (sync): {response_text}")

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 404:
            self.logger.error(
                f"Not Found Error (sync) - Status: {response.status_code}, Message: {response_text}"
            )
            raise NotFoundError(response_text)
        elif response.status_code == 422:
            self.logger.error(
                f"Validation Error (sync) - Status: {response.status_code}, Message: {response_text}"
            )
            raise ValidationError(response_text)
        else:
            self.logger.error(
                f"API Error (sync) - Status: {response.status_code}, Message: {response_text}"
            )
            raise APIError(response.status_code, response_text)
