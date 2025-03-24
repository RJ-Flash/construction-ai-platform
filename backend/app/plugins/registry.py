"""
Plugin Registry System

This module provides a central registry for plugins in the system.
"""
from typing import Dict, Type, Optional, List


# Global plugin registry
_plugin_registry: Dict[str, Type] = {}


def register_plugin(plugin_class):
    """
    Decorator to register a plugin class with the registry.
    
    Args:
        plugin_class: The plugin class to register.
        
    Returns:
        The plugin class, unchanged.
    """
    # Create an instance of the plugin class to get its ID
    plugin_instance = plugin_class()
    plugin_id = plugin_instance.id
    
    # Register the plugin class
    _plugin_registry[plugin_id] = plugin_class
    
    return plugin_class


def get_plugin_by_id(plugin_id: str) -> Optional[Type]:
    """
    Gets a plugin class by its ID.
    
    Args:
        plugin_id: The ID of the plugin to get.
        
    Returns:
        The plugin class or None if not found.
    """
    return _plugin_registry.get(plugin_id)


def get_all_plugins() -> Dict[str, Type]:
    """
    Gets all registered plugins.
    
    Returns:
        A dictionary mapping plugin IDs to plugin classes.
    """
    return _plugin_registry.copy()


def get_plugins_by_category(category: str) -> Dict[str, Type]:
    """
    Gets all plugins in a specific category.
    
    Args:
        category: The category to filter by.
        
    Returns:
        A dictionary mapping plugin IDs to plugin classes for the given category.
    """
    return {
        plugin_id: plugin_class
        for plugin_id, plugin_class in _plugin_registry.items()
        if plugin_class().category == category
    }


def get_plugin_categories() -> List[str]:
    """
    Gets a list of all plugin categories.
    
    Returns:
        A list of unique plugin categories.
    """
    return list(set(plugin_class().category for plugin_class in _plugin_registry.values()))
