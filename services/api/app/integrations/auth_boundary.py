"""Phase 7 — External Authentication Boundary.

Secrets-management boundary that separates adapter code from credential
access.  Adapters NEVER receive raw API keys or tokens — they receive
opaque AuthToken objects that the boundary resolves at call time.

Secret resolution order:
  1. Environment variable (e.g. PROVIDER_<UPPER_ID>_SECRET)
  2. Secrets file (future: HashiCorp Vault / AWS Secrets Manager)
  3. Fallback to None (adapter must fail gracefully)

Rule:  No raw secret value is ever written to logs, database, or
       response bodies — only redacted sentinel strings are allowed.
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from app.integrations.contracts import AuthMethod

logger = logging.getLogger(__name__)

_REDACTED = "[REDACTED]"


# ---------------------------------------------------------------------------
# Auth Token — opaque handle, never exposes raw secret
# ---------------------------------------------------------------------------


@dataclass
class AuthToken:
    method: AuthMethod
    provider_id: str
    issued_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    _raw: str = field(default="", repr=False)  # Never surfaces in repr / logs

    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now(UTC) > self.expires_at

    def to_header(self) -> str:
        """Return the HTTP Authorization header value (never logs the raw value)."""
        match self.method:
            case AuthMethod.API_KEY:
                return f"ApiKey {_REDACTED}"
            case AuthMethod.OAUTH2:
                return f"Bearer {_REDACTED}"
            case AuthMethod.JWT_CLIENT:
                return f"Bearer {_REDACTED}"
            case _:
                return f"{self.method.value} {_REDACTED}"

    def _raw_header(self) -> str:
        """Internal use only — returns the real header value, NEVER logged."""
        match self.method:
            case AuthMethod.API_KEY:
                return f"ApiKey {self._raw}"
            case AuthMethod.OAUTH2 | AuthMethod.JWT_CLIENT:
                return f"Bearer {self._raw}"
            case AuthMethod.NONE:
                return ""
            case _:
                return f"{self.method.value} {self._raw}"


# ---------------------------------------------------------------------------
# Credential Manager — resolves secrets from the environment boundary
# ---------------------------------------------------------------------------


class CredentialManager:
    """
    Resolves provider secrets from the environment.

    Convention:  Secret env var name = PROVIDER_{UPPER_PROVIDER_ID}_SECRET
    e.g. provider_id="cbse-001"  →  env var PROVIDER_CBSE_001_SECRET

    In development / mock mode the manager returns a dummy token so that
    adapters can operate without real secrets.
    """

    def __init__(self, environment: str = "development") -> None:
        self._environment = environment
        self._token_cache: dict[str, AuthToken] = {}

    def _env_key(self, provider_id: str) -> str:
        safe = provider_id.upper().replace("-", "_").replace(".", "_")
        return f"PROVIDER_{safe}_SECRET"

    def _resolve_secret(self, provider_id: str) -> str | None:
        env_key = self._env_key(provider_id)
        value = os.environ.get(env_key)
        if value:
            return value
        # In development fall back to a deterministic dummy secret
        if self._environment == "development":
            return f"dev-mock-secret-{provider_id}"
        return None

    def get_token(self, provider_id: str, method: AuthMethod) -> AuthToken:
        # Return cached non-expired token
        cached = self._token_cache.get(provider_id)
        if cached and not cached.is_expired():
            return cached

        if method == AuthMethod.NONE:
            token = AuthToken(method=AuthMethod.NONE, provider_id=provider_id, _raw="")
            self._token_cache[provider_id] = token
            return token

        raw_secret = self._resolve_secret(provider_id)
        if raw_secret is None:
            raise RuntimeError(
                f"No credential found for provider '{provider_id}'. "
                f"Set env var '{self._env_key(provider_id)}'."
            )

        token = AuthToken(
            method=method,
            provider_id=provider_id,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            _raw=raw_secret,
        )
        self._token_cache[provider_id] = token
        logger.debug("Issued auth token for provider '%s' (method=%s)", provider_id, method.value)
        return token

    def invalidate(self, provider_id: str) -> None:
        self._token_cache.pop(provider_id, None)


# ---------------------------------------------------------------------------
# Adapter Authenticator — attaches auth to outgoing requests
# ---------------------------------------------------------------------------


class AdapterAuthenticator:
    """
    Assembles HTTP headers or context for outgoing provider requests.

    Usage:
        authenticator = AdapterAuthenticator(credential_manager)
        headers = authenticator.build_headers(provider_id, auth_method)
        # Pass headers to httpx / requests — raw secret is in headers dict
        # but NEVER logged by this class.
    """

    def __init__(self, credential_manager: CredentialManager) -> None:
        self._cm = credential_manager

    def build_headers(self, provider_id: str, method: AuthMethod) -> dict[str, str]:
        token = self._cm.get_token(provider_id, method)
        raw = token._raw_header()  # noqa: SLF001
        if not raw:
            return {}
        return {"Authorization": raw}

    def sign_request_body(self, provider_id: str, body: bytes) -> str:
        """HMAC-SHA256 signature for signed-request auth method."""
        token = self._cm.get_token(provider_id, AuthMethod.SIGNED_REQUEST)
        secret = token._raw.encode()  # noqa: SLF001
        return hmac.new(secret, body, hashlib.sha256).hexdigest()

    def verify_inbound_signature(
        self, provider_id: str, body: bytes, signature: str
    ) -> bool:
        """Verify HMAC-SHA256 on an inbound webhook payload."""
        try:
            token = self._cm.get_token(provider_id, AuthMethod.API_KEY)
            secret = token._raw.encode()  # noqa: SLF001
            expected = hmac.new(secret, body, hashlib.sha256).hexdigest()
            return hmac.compare_digest(expected, signature)
        except Exception:
            return False


# ---------------------------------------------------------------------------
# Module-level singletons
# ---------------------------------------------------------------------------

_ENV = os.environ.get("DIGIIN_ENVIRONMENT", "development")
credential_manager = CredentialManager(environment=_ENV)
adapter_authenticator = AdapterAuthenticator(credential_manager)
