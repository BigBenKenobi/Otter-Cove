from __future__ import annotations

from collections.abc import Mapping, Sequence
from urllib.parse import parse_qsl, unquote, urlsplit

from .errors import PersistencePolicyError

# Structured configuration, rather than arbitrary document/message prose, is the
# policy surface. Exact normalized names preserve legitimate `token_limit` values.
_SECRET_KEYS = {"password", "passwd", "secret", "api_key", "apikey", "private_key", "credential", "auth_key", "access_token", "refresh_token"}
_ENDPOINT_KEYS = {"endpoint", "url", "base_url", "api_url"}


def _name(value: object) -> str:
    """Normalize structured field names without broad substring matching."""

    return unquote(str(value)).strip().casefold().replace("-", "_").replace(" ", "_")


def assert_safe_endpoint(value: object, *, path: str) -> None:
    """Reject URL userinfo and credential query names without exposing values."""

    if not isinstance(value, str):
        raise PersistencePolicyError(f"Structured endpoint '{path}' must be text.")
    try:
        parsed = urlsplit(value)
    except ValueError as exc:
        raise PersistencePolicyError(f"Structured endpoint '{path}' is malformed.") from exc
    if parsed.username is not None or parsed.password is not None:
        raise PersistencePolicyError(f"Structured endpoint '{path}' cannot include userinfo.")
    if any(_name(key) in _SECRET_KEYS for key, _value in parse_qsl(parsed.query, keep_blank_values=True)):
        raise PersistencePolicyError(f"Structured endpoint '{path}' has a credential query parameter.")


def assert_no_credentials(value, *, path: str = "data") -> None:
    """Reject structured credentials without scanning arbitrary free-text content."""
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = _name(key)
            if normalized in _SECRET_KEYS:
                raise PersistencePolicyError(
                    f"Credential field '{path}.{key}' cannot be stored in ordinary application data."
                )
            if normalized in _ENDPOINT_KEYS:
                assert_safe_endpoint(child, path=f"{path}.{key}")
            elif isinstance(child, (Mapping, Sequence)) and not isinstance(child, (str, bytes, bytearray)):
                assert_no_credentials(child, path=f"{path}.{key}")
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            assert_no_credentials(child, path=f"{path}[{index}]")
