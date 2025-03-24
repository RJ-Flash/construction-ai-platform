"""
Electrical Systems Plugin

This plugin analyzes electrical specifications and extracts structured data.
"""
from typing import Dict, Any

from app.plugins.mep.base import MEPPlugin
from app.plugins.registry import register_plugin


@register_plugin
class ElectricalSystemsPlugin(MEPPlugin):
    """
    Plugin for analyzing electrical systems specifications.
    """
    
    @property
    def id(self) -> str:
        return "mep.electrical_systems"
    
    @property
    def name(self) -> str:
        return "Electrical Systems Estimator"
    
    @property
    def description(self) -> str:
        return "Analyzes electrical specifications and extracts structured data about electrical systems."
    
    @property
    def price(self) -> float:
        return 199.0
    
    def _get_analysis_prompt(self, text: str) -> str:
        """
        Creates a prompt for electrical systems analysis.
        
        Args:
            text: The text to analyze.
            
        Returns:
            The prompt to send to OpenAI.
        """
        return f"""
        Analyze the following construction document text and extract all information related to electrical systems.
        Focus on:
        
        1. Electrical service (size, voltage, phases, etc.)
        2. Distribution equipment (panels, switchgear, etc.)
        3. Lighting systems (types, quantities, controls)
        4. Power systems (receptacles, circuits)
        5. Low voltage systems (data, security, fire alarm)
        6. Emergency power systems
        
        Return the information as a structured JSON object with appropriate nested properties.
        Only include information that is explicitly mentioned in the text.
        
        TEXT TO ANALYZE:
        {text}
        """
