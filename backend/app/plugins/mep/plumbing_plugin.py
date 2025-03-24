"""
Plumbing Systems Plugin

This plugin analyzes plumbing specifications and extracts structured data.
"""
from typing import Dict, Any

from app.plugins.mep.base import MEPPlugin
from app.plugins.registry import register_plugin


@register_plugin
class PlumbingSystemsPlugin(MEPPlugin):
    """
    Plugin for analyzing plumbing systems specifications.
    """
    
    @property
    def id(self) -> str:
        return "mep.plumbing_systems"
    
    @property
    def name(self) -> str:
        return "Plumbing Systems Estimator"
    
    @property
    def description(self) -> str:
        return "Analyzes plumbing specifications and extracts structured data about plumbing systems."
    
    @property
    def price(self) -> float:
        return 199.0
    
    def _get_analysis_prompt(self, text: str) -> str:
        """
        Creates a prompt for plumbing systems analysis.
        
        Args:
            text: The text to analyze.
            
        Returns:
            The prompt to send to OpenAI.
        """
        return f"""
        Analyze the following construction document text and extract all information related to plumbing systems.
        Focus on:
        
        1. Water supply systems (domestic cold, domestic hot, recirculation)
        2. Sanitary systems (drainage, venting)
        3. Plumbing fixtures (toilets, sinks, showers, drinking fountains, etc.)
        4. Water heating systems
        5. Special plumbing systems (gas, compressed air, etc.)
        
        Return the information as a structured JSON object with appropriate nested properties.
        Only include information that is explicitly mentioned in the text.
        
        TEXT TO ANALYZE:
        {text}
        """
