"""
MEP Plugins Package

This package contains plugins for Mechanical, Electrical, and Plumbing (MEP) systems.
"""

# Import plugins to register them with the registry
from app.plugins.mep.electrical_plugin import ElectricalSystemsPlugin
from app.plugins.mep.plumbing_plugin import PlumbingSystemsPlugin
from app.plugins.mep.hvac_plugin import HVACSystemsPlugin

__all__ = [
    "ElectricalSystemsPlugin",
    "PlumbingSystemsPlugin", 
    "HVACSystemsPlugin"
]
