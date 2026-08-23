"""
DigiIn Core Security Subsystem
Provides centralized identity, authorization, file security, rate limiting, and error handling.
"""

from .auth_security import AccountState, AuthenticationSecurityService
from .authorization import ROLE_PERMISSIONS, AuthorizationService, Permission, Role
from .error_handling import DigiInErrorCode, DigiInSecurityException, format_error_response
from .file_security import FileSecurityService
from .rate_limiting import RATE_LIMIT_TIERS, RateLimiterService

__all__ = [
    "AuthenticationSecurityService",
    "AccountState",
    "AuthorizationService",
    "Role",
    "Permission",
    "ROLE_PERMISSIONS",
    "FileSecurityService",
    "RateLimiterService",
    "RATE_LIMIT_TIERS",
    "DigiInErrorCode",
    "DigiInSecurityException",
    "format_error_response",
]
