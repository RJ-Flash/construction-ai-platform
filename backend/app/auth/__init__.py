"""
Auth Package

This package contains the authentication functionality for the Construction AI Platform.
"""

from app.auth.dependencies import get_current_user, User

__all__ = ["get_current_user", "User"]
