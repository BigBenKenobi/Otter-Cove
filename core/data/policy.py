from __future__ import annotations

from collections.abc import Mapping, Sequence

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
