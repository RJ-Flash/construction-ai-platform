from typing import Dict, List, Optional, Any, Type
import os
import importlib
import json
import logging
import pkgutil
from .base import AnalysisPlugin

logger = logging.getLogger(__name__)

# Global plugin registry
_PLUGINS: Dict[str, Type[AnalysisPlugin]] = {}

def register_plugin(plugin_class: Type[AnalysisPlugin]) -> Type[AnalysisPlugin]:
    """
    Register a plugin class with the registry.
    Can be used as a decorator.
    
    Args:
        plugin_class: Plugin class to register
        
    Returns:
        The plugin class (for decorator usage)
    """
    if not plugin_class.id:
        raise ValueError(f"Plugin class {plugin_class.__name__} has no ID")
    
    if plugin_class.id in _PLUGINS:
        logger.warning(f"Plugin with ID '{plugin_class.id}' already registered, overwriting")
    
    _PLUGINS[plugin_class.id] = plugin_class
    logger.info(f"Registered plugin class: {plugin_class.__name__} (ID: {plugin_class.id})")
    
    return plugin_class

def get_plugin_by_id(plugin_id: str) -> Optional[Type[AnalysisPlugin]]:
    """
    Get a plugin class by ID.
    
    Args:
        plugin_id: ID of the plugin
        
    Returns:
        Plugin class or None if not found
    """
    return _PLUGINS.get(plugin_id)

def get_available_plugins() -> List[Dict[str, Any]]:
    """
    Get a list of all available plugins with their metadata.
    
    Returns:
        List of plugin metadata
    """
    result = []
    
    for plugin_id, plugin_class in _PLUGINS.items():
        # Create a temporary instance to get metadata
        plugin = plugin_class()
        result.append(plugin.metadata)
    
    return result

def discover_plugins() -> None:
    """
    Discover and load plugins from the plugins directory.
    """
    # Get the current directory (where this file is)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Walk through all packages in the plugins directory
    for _, name, ispkg in pkgutil.iter_modules([current_dir]):
        # Skip base modules and non-packages
        if name in ['base', 'registry', '__pycache__'] or not ispkg:
            continue
        
        try:
            # Import the module
            module_name = f"app.plugins.{name}"
            importlib.import_module(module_name)
            logger.info(f"Discovered plugin module: {module_name}")
        except Exception as e:
            logger.error(f"Error loading plugin module {name}: {str(e)}")

# Auto-discover plugins when the registry is imported
discover_plugins()