"""
Base Plugin Class

This module provides the base class for all plugins in the system.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class Plugin(ABC):
    """
    Base class for all plugins in the system.
    """
    
    @property
    @abstractmethod
    def id(self) -> str:
        """
        The unique identifier for this plugin.
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """
        The display name for this plugin.
        """
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """
        A brief description of what this plugin does.
        """
        pass
    
    @property
    @abstractmethod
    def category(self) -> str:
        """
        The category this plugin belongs to.
        """
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """
        The version of this plugin.
        """
        pass
    
    @property
    @abstractmethod
    def price(self) -> float:
        """
        The price of this plugin.
        """
        pass
    
    @abstractmethod
    async def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyzes the provided text and returns a structured dictionary
        containing the extracted data.
        
        Args:
            text: The text to analyze.
            
        Returns:
            A dictionary containing the structured data extracted from the text.
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Gets the metadata for this plugin.
        
        Returns:
            A dictionary containing the plugin metadata.
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "version": self.version,
            "price": self.price,
        }
