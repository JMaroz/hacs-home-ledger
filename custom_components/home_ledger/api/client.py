"""Config-flow validation client for home_ledger."""

import aiohttp


class HomeLedgerApiClientError(Exception):
    """Base exception to indicate a validation error."""


class HomeLedgerApiClientCommunicationError(HomeLedgerApiClientError):
    """Exception to indicate a communication error."""


class HomeLedgerApiClientAuthenticationError(HomeLedgerApiClientError):
    """Exception to indicate an authentication error."""


class HomeLedgerApiClient:
    """No-op validator for the local ledger integration."""

    def __init__(self, username: str, password: str, session: aiohttp.ClientSession) -> None:
        """Initialize the validation client."""
        self._username = username
        self._password = password
        self._session = session

    async def async_get_data(self) -> dict[str, str]:
        """Validate the configured entry can be created."""
        return {"username": self._username}
