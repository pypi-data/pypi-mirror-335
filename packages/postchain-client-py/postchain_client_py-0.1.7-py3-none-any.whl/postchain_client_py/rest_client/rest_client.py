import asyncio
from ctypes import Union
from typing import Optional, Dict, Any
from dataclasses import dataclass
import aiohttp
import logging
from ..blockchain_client.enums import Method

logger = logging.getLogger(__name__)

@dataclass
class Response:
    status_code: int = 404  # Default to error status code
    body: Optional[Dict[str, Any]] = None
    error: Optional[Exception] = None

    @classmethod
    def error_response(cls, error: Exception) -> 'Response':
        """Create an error response"""
        return cls(
            status_code=500,
            body=None,
            error=error
        )

class RestClient:
    def __init__(self, config):
        self.config = config
        self._session = None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def request_with_failover(
        self,
        method: Method,
        endpoint: str,
        data: Any = None,
        headers: Dict[str, str] = None
    ) -> Response:
        """Make request with failover strategy"""
        for endpoint_url in self.config.node_urls:
            for attempt in range(self.config.attempts_per_endpoint):
                try:
                    response = await self._make_request(
                        method,
                        f"{endpoint_url}/{endpoint}",
                        data,
                        headers
                    )
                    logger.info("Response on failover attempt: %s", response)
                    if response.status_code == 200:
                        if isinstance(response.body, dict):
                            if 'status' in response.body:
                                if response.body['status'] == 'unknown':
                                    logger.debug("Transaction unknown, retrying...")
                                    await asyncio.sleep(self.config.attempt_interval / 1000)
                                    continue
                        return response
                    if response.status_code == 404 or response.status_code == 400:
                        if isinstance(response.body, dict):
                            if 'error' in response.body:
                                logger.debug("Error: %s", response.body['error'])
                                return Response.error_response(Exception(response.body['error']))
                        else:
                            logger.debug("Error: %s", response.body)
                            error_msg = "Cannot find transaction or unknown error"
                            if isinstance(response.body, dict):
                                error_msg += f": {response.body}"
                            else: 
                                error_msg += f": {response}"
                            return Response.error_response(Exception(error_msg))
                except Exception as e:
                    logger.warning(f"Request failed: {str(e)}")
                    if attempt == self.config.attempts_per_endpoint - 1:
                        logger.error("All attempts failed: %s", e)
                        return Response.error_response(e)
        
        return Response.error_response(Exception("All attempts failed"))

    async def _make_request(
        self,
        method: Method,
        url: str,
        data: Any = None,
        headers: Dict[str, str] = None
    ) -> Response:
        """Make a single request"""
        session = await self._get_session()
        default_headers = {
            'Content-Type': 'application/octet-stream'  # Changed for binary data
        }
        headers = {**default_headers, **(headers or {})}

        try:
            # Configure SSL context based on URL scheme
            # Use data parameter instead of json for binary data
            async with session.request(
                method.value,
                url,
                data=data if isinstance(data, bytes) else None,  # Only send if bytes
                json=None if isinstance(data, bytes) else data,  # Use json for non-binary
                headers=headers,
                ssl=True if url.startswith('https://') else False,  # Only use SSL for HTTPS
            ) as response:
                try:
                    response_data = await response.json()
                except:
                    response_data = await response.read()
                
                logger.debug("Response data: %s", response_data)
                await self.close()
                return Response(
                    status_code=response.status,
                    body=response_data
                )
        except Exception as e:
            await self.close()
            return Response.error_response(e)

    async def close(self):
        """Close the client session"""
        if self._session and not self._session.closed:
            await self._session.close() 