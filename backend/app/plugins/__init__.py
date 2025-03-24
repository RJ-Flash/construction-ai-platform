"""
Plugins Package

This package contains the plugin system for the Construction AI Platform.
"""

# Import all plugin packages to register them with the registry
import app.plugins.mep

# Import registry functions for easy access
from app.plugins.registry import (
    get_plugin_by_id,
    get_all_plugins,
    get_plugins_by_category,
    get_plugin_categories
)

__all__ = [
    "get_plugin_by_id",
    "get_all_plugins",
    "get_plugins_by_category",
    "get_plugin_categories"
]
