"""
API package for home_ledger.

Exception hierarchy:
    HomeLedgerApiClientError (base)
    ├── HomeLedgerApiClientCommunicationError (network/timeout)
    └── HomeLedgerApiClientAuthenticationError (401/403)

The coordinator maps them onto ConfigEntryAuthFailed and UpdateFailed; nothing else
in the integration imports this package.
"""

from .client import (
    FAN_SPEEDS,
    HomeLedgerApiClient,
    HomeLedgerApiClientAuthenticationError,
    HomeLedgerApiClientCommunicationError,
    HomeLedgerApiClientError,
)

__all__ = [
    "FAN_SPEEDS",
    "HomeLedgerApiClient",
    "HomeLedgerApiClientAuthenticationError",
    "HomeLedgerApiClientCommunicationError",
    "HomeLedgerApiClientError",
]
