"""HTTP client for Dooray API communication."""

import logging
from typing import Any, Dict, Optional

import aiohttp


class DoorayHttpClient:
    """HTTP client for communicating with Dooray API."""

    def __init__(self, base_url: str, api_key: str) -> None:
        """Initialize the Dooray HTTP client.
        
        Args:
            base_url: Dooray API base URL
            api_key: Dooray API key
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        
        # Default headers for all requests
        self.headers = {
            "Authorization": f"dooray-api {api_key}",
            "Content-Type": "application/json",
        }

    async def get(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a GET request to Dooray API.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            
        Returns:
            API response as dictionary
            
        Raises:
            aiohttp.ClientError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        self.logger.debug(f"GET {url} with params: {params}")
        
        async with aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    self.logger.debug(f"Response: {data}")
                    return data
                else:
                    error_text = await response.text()
                    self.logger.error(f"API error {response.status}: {error_text}")
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=error_text
                    )

    async def post(
        self, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a POST request to Dooray API.
        
        Args:
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            
        Returns:
            API response as dictionary
            
        Raises:
            aiohttp.ClientError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        self.logger.debug(f"POST {url} with data: {data}, params: {params}")
        
        async with aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            async with session.post(url, json=data, params=params) as response:
                if response.status in (200, 201):
                    data = await response.json()
                    self.logger.debug(f"Response: {data}")
                    return data
                else:
                    error_text = await response.text()
                    self.logger.error(f"API error {response.status}: {error_text}")
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=error_text
                    )

    async def put(
        self, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a PUT request to Dooray API.
        
        Args:
            endpoint: API endpoint (without base URL)
            data: Request body data
            params: Query parameters
            
        Returns:
            API response as dictionary
            
        Raises:
            aiohttp.ClientError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        self.logger.debug(f"PUT {url} with data: {data}, params: {params}")
        
        async with aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            async with session.put(url, json=data, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    self.logger.debug(f"Response: {data}")
                    return data
                else:
                    error_text = await response.text()
                    self.logger.error(f"API error {response.status}: {error_text}")
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=error_text
                    )

    async def delete(
        self, 
        endpoint: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Make a DELETE request to Dooray API.
        
        Args:
            endpoint: API endpoint (without base URL)
            params: Query parameters
            
        Returns:
            API response as dictionary
            
        Raises:
            aiohttp.ClientError: If request fails
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        self.logger.debug(f"DELETE {url} with params: {params}")
        
        async with aiohttp.ClientSession(
            headers=self.headers,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            async with session.delete(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    self.logger.debug(f"Response: {data}")
                    return data
                else:
                    error_text = await response.text()
                    self.logger.error(f"API error {response.status}: {error_text}")
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=error_text
                    )