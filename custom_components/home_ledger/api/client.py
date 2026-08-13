"""API client for home_ledger."""

import asyncio
import socket
from typing import Any

import aiohttp

API_URL = "https://jsonplaceholder.typicode.com/posts/1"
REQUEST_TIMEOUT = 10


class HomeLedgerApiClientError(Exception):
    """Base exception to indicate a general API error."""


class HomeLedgerApiClientCommunicationError(
    HomeLedgerApiClientError,
):
    """Exception to indicate a communication error with the API."""


class HomeLedgerApiClientAuthenticationError(
    HomeLedgerApiClientError,
):
    """Exception to indicate an authentication error with the API."""


def _verify_response_or_raise(response: aiohttp.ClientResponse) -> None:
    """
    Verify that the API response is valid.

    Raises:
        HomeLedgerApiClientAuthenticationError: For 401 and 403 responses.
        aiohttp.ClientResponseError: For every other unsuccessful status.

    """
    if response.status in (401, 403):
        msg = "Invalid credentials"
        raise HomeLedgerApiClientAuthenticationError(msg)
    response.raise_for_status()


class HomeLedgerApiClient:
    """
    Stand-in for the client of a real device or service.

    JSONPlaceholder is queried so that a real request happens on every poll, and its
    response is turned into a device-shaped payload for the sensors.
    """

    def __init__(
        self,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        """Initialize the API client."""
        self._username = username
        self._password = password
        self._session = session

    async def async_get_data(self) -> dict[str, Any]:
        """
        Fetch the current device state.

        Returns:
            The device state, keyed the way entities read it.

        """
        response = await self._api_wrapper(method="get", url=API_URL)
        return self._build_payload(response)

    def _build_payload(self, response: dict[str, Any]) -> dict[str, Any]:
        """Derive a device-shaped payload from the demo endpoint's response."""
        seed = int(response.get("userId", 1)) * 47 + int(response.get("id", 1)) * 13
        return {
            "model": "Home Ledger",
            "serial_number": f"BP-{seed:06d}",
            "sw_version": "1.4.2",
            "air_quality_index": seed % 501,
            "pm25": round((seed * 0.37) % 300, 1),
        }

    async def _api_wrapper(
        self,
        method: str,
        url: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """
        Perform a request and translate transport errors into client exceptions.

        Returns:
            The decoded JSON response.

        Raises:
            HomeLedgerApiClientAuthenticationError: If the credentials are rejected.
            HomeLedgerApiClientCommunicationError: If the request does not complete.
            HomeLedgerApiClientError: For any other failure.

        """
        try:
            async with asyncio.timeout(REQUEST_TIMEOUT):
                response = await self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data,
                )
                _verify_response_or_raise(response)
                return await response.json()

        except TimeoutError as exception:
            msg = f"Timeout error fetching information - {exception}"
            raise HomeLedgerApiClientCommunicationError(msg) from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            msg = f"Error fetching information - {exception}"
            raise HomeLedgerApiClientCommunicationError(msg) from exception
        except HomeLedgerApiClientError:
            raise
        except Exception as exception:
            msg = f"Unexpected error talking to the API - {exception}"
            raise HomeLedgerApiClientError(msg) from exception
