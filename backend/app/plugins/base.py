from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Set, Type
import importlib
import os
import json
import logging

logger = logging.getLogger(__name__)

class AnalysisPlugin(ABC):
    """Base class for all analysis plugins."""
    
    # Plugin metadata
    id: str = ""
    name: str = ""
    version: str = "0.1.0"
    description: str = ""
    author: str = ""
    category: str = "general"
    price: float = 0.0
    
    # Required document types
    supported_file_types: Set[str] = {"pdf", "jpg", "png"}
    
    @abstractmethod
    async def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze the document text and extract relevant information.
        
        Args:
            text: Document text content
            context: Additional context information
            
        Returns:
            Dictionary containing extracted information
        """
        pass
    
    @abstractmethod
    def get_prompts(self) -> Dict[str, str]:
        """
        Get the prompts used by this plugin.
        
        Returns:
            Dictionary of prompt templates
        """
        pass
    
    @property
    def metadata(self) -> Dict[str, Any]:
        """
        Get plugin metadata.
        
        Returns:
            Dictionary containing plugin metadata
        """
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "category": self.category,
            "price": self.price,
            "supported_file_types": list(self.supported_file_types)
        }
    
    def validate_input(self, text: str) -> bool:
        """
        Validate the input text.
        
        Args:
            text: Document text content
            
        Returns:
            True if the input is valid, False otherwise
        """
        # Basic validation - check if text is not empty
        return bool(text and text.strip())
    
    def format_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the analysis results.
        
        Args:
            results: Raw analysis results
            
        Returns:
            Formatted results
        """
        # Base implementation just passes through results
        return results


class PluginManager:
    """Manager for loading and running analysis plugins."""
    
    def __init__(self):
        self.plugins: Dict[str, AnalysisPlugin] = {}
        self.enabled_plugins: Set[str] = set()
    
    def register_plugin(self, plugin_instance: AnalysisPlugin) -> None:
        """
        Register a plugin with the manager.
        
        Args:
            plugin_instance: Instance of an AnalysisPlugin
        """
        if not plugin_instance.id:
            raise ValueError("Plugin ID cannot be empty")
            
        self.plugins[plugin_instance.id] = plugin_instance
        logger.info(f"Registered plugin: {plugin_instance.name} (ID: {plugin_instance.id})")
    
    def enable_plugin(self, plugin_id: str) -> None:
        """
        Enable a plugin.
        
        Args:
            plugin_id: ID of the plugin to enable
        """
        if plugin_id not in self.plugins:
            raise ValueError(f"Plugin with ID '{plugin_id}' not found")
            
        self.enabled_plugins.add(plugin_id)
        logger.info(f"Enabled plugin: {plugin_id}")
    
    def disable_plugin(self, plugin_id: str) -> None:
        """
        Disable a plugin.
        
        Args:
            plugin_id: ID of the plugin to disable
        """
        if plugin_id in self.enabled_plugins:
            self.enabled_plugins.remove(plugin_id)
            logger.info(f"Disabled plugin: {plugin_id}")
    
    def get_plugin(self, plugin_id: str) -> Optional[AnalysisPlugin]:
        """
        Get a plugin by ID.
        
        Args:
            plugin_id: ID of the plugin
            
        Returns:
            Plugin instance or None if not found
        """
        return self.plugins.get(plugin_id)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """
        List all registered plugins.
        
        Returns:
            List of plugin metadata
        """
        return [
            {**plugin.metadata, "enabled": plugin.id in self.enabled_plugins}
            for plugin in self.plugins.values()
        ]
    
    def list_enabled_plugins(self) -> List[Dict[str, Any]]:
        """
        List all enabled plugins.
        
        Returns:
            List of enabled plugin metadata
        """
        return [
            plugin.metadata
            for plugin_id, plugin in self.plugins.items()
            if plugin_id in self.enabled_plugins
        ]
    
    async def run_analysis(self, text: str, plugin_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run analysis using a specific plugin.
        
        Args:
            text: Document text content
            plugin_id: ID of the plugin to use
            context: Additional context information
            
        Returns:
            Analysis results
        """
        plugin = self.get_plugin(plugin_id)
        
        if not plugin:
            raise ValueError(f"Plugin with ID '{plugin_id}' not found")
            
        if plugin_id not in self.enabled_plugins:
            raise ValueError(f"Plugin with ID '{plugin_id}' is not enabled")
            
        if not plugin.validate_input(text):
            raise ValueError("Invalid input text for analysis")
            
        # Run the analysis
        results = await plugin.analyze(text, context)
        
        # Format the results
        return plugin.format_results(results)
    
    async def run_all_enabled_plugins(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Dict[str, Any]]:
        """
        Run analysis using all enabled plugins.
        
        Args:
            text: Document text content
            context: Additional context information
            
        Returns:
            Dictionary mapping plugin IDs to their analysis results
        """
        results = {}
        
        for plugin_id in self.enabled_plugins:
            try:
                plugin_results = await self.run_analysis(text, plugin_id, context)
                results[plugin_id] = plugin_results
            except Exception as e:
                logger.error(f"Error running plugin {plugin_id}: {str(e)}")
                results[plugin_id] = {"error": str(e)}
                
        return results