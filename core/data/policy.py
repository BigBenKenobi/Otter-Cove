from __future__ import annotations

from collections.abc import Mapping, Sequence
from urllib.parse import parse_qsl, unquote, urlsplit

from .errors import PersistencePolicyError

# Credentials deliberately have no ordinary repository/table in the GUI milestone.
_SECRET_MARKERS = (
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "private_key",
    "credential",
    "auth_key",
)


def assert_no_credentials(value, *, path: str = "data") -> None:
    """Reject values that look like credentials before they reach SQLite/export JSON."""
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).strip().lower().replace("-", "_").replace(" ", "_")
            if any(marker in normalized for marker in _SECRET_MARKERS):
                raise PersistencePolicyError(
                    f"Credential-like field '{path}.{key}' cannot be stored in ordinary application data."
                )
            assert_no_credentials(child, path=f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            assert_no_credentials(child, path=f"{path}[{index}]")


def assert_safe_endpoint(endpoint: str, *, path: str = "model.endpoint") -> None:
    """Reject endpoint URLs that could persist credentials in ordinary data.

    Model endpoints are exported with the registry, so URL userinfo and query
    pairs containing credential markers are prohibited even when the URL itself
    is otherwise syntactically valid. Provider secrets must later flow through a
    dedicated secure adapter rather than SQLite or local-data JSON.
    """

    parsed = urlsplit(endpoint)
    if parsed.username is not None or parsed.password is not None:
        raise PersistencePolicyError(
            f"Credential-like URL userinfo in '{path}' cannot be stored in ordinary application data."
        )
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        # Decode once more to catch nested values such as ``next=api_key%3D...``.
        candidate = f"{unquote(key)} {unquote(value)}".strip().lower().replace("-", "_").replace(" ", "_")
        if any(marker in candidate for marker in _SECRET_MARKERS):
            raise PersistencePolicyError(
                f"Credential-like query data in '{path}' cannot be stored in ordinary application data."
            )
