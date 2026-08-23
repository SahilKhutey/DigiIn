from __future__ import annotations

from app.core.config import Settings, get_settings
from app.integrations.auth.base import AuthenticatedSubject, AuthProvider
from app.integrations.auth.demo import DemoAuthProvider
from app.integrations.auth.production import ProductionAuthProvider


def get_auth_provider(settings: Settings | None = None) -> AuthProvider:
    """Factory to resolve configured authentication provider according to environment."""
    current_settings = settings or get_settings()
    if current_settings.environment == "production":
        return ProductionAuthProvider(auth_secret=current_settings.auth_secret)
    return DemoAuthProvider()


__all__ = [
    "AuthenticatedSubject",
    "AuthProvider",
    "DemoAuthProvider",
    "ProductionAuthProvider",
    "get_auth_provider",
]
