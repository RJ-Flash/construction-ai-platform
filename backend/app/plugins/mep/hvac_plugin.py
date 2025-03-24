"""
HVAC Systems Plugin

This plugin analyzes HVAC specifications and extracts structured data.
"""
from typing import Dict, Any

from app.plugins.mep.base import MEPPlugin
from app.plugins.registry import register_plugin


@register_plugin
class HVACSystemsPlugin(MEPPlugin):
    """
    Plugin for analyzing HVAC systems specifications.
    """
    
    @property
    def id(self) -> str:
        return "mep.hvac_systems"
    
    @property
    def name(self) -> str:
        return "HVAC & Mechanical Estimator"
    
    @property
    def description(self) -> str:
        return "Analyzes HVAC and mechanical specifications and extracts structured data about these systems."
    
    @property
    def price(self) -> float:
        return 249.0
    
    def _get_analysis_prompt(self, text: str) -> str:
        """
        Creates a prompt for HVAC systems analysis.
        
        Args:
            text: The text to analyze.
            
        Returns:
            The prompt to send to OpenAI.
        """
        return f"""
        Analyze the following construction document text and extract all information related to HVAC and mechanical systems.
        Focus on:
        
        1. Heating systems (boilers, furnaces, heat pumps, etc.)
        2. Cooling systems (chillers, condensers, cooling towers, etc.)
        3. Air handling units and fans
        4. Ventilation systems (energy recovery, makeup air, etc.)
        5. Ductwork and piping
        6. Controls and building automation systems
        
        Return the information as a structured JSON object with appropriate nested properties.
        Only include information that is explicitly mentioned in the text.
        
        TEXT TO ANALYZE:
        {text}
        """
