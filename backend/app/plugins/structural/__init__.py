"""
Structural Plugins Package

This package contains plugins for structural analysis of construction documents.
"""

# Import plugins to register them with the registry
from app.plugins.structural.foundation_plugin import FoundationAnalysisPlugin
from app.plugins.structural.framing_plugin import FramingAnalysisPlugin
from app.plugins.structural.load_plugin import LoadAnalysisPlugin

__all__ = [
    "FoundationAnalysisPlugin",
    "FramingAnalysisPlugin",
    "LoadAnalysisPlugin"
]
