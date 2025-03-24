"""
Load Analysis Plugin

This plugin analyzes structural load specifications and extracts structured data.
"""
from typing import Dict, Any

from app.plugins.structural.base import StructuralPlugin
from app.plugins.registry import register_plugin


@register_plugin
class LoadAnalysisPlugin(StructuralPlugin):
    """
    Plugin for analyzing structural load specifications.
    """
    
    @property
    def id(self) -> str:
        return "structural.load_analysis"
    
    @property
    def name(self) -> str:
        return "Structural Load Analysis"
    
    @property
    def description(self) -> str:
        return "Analyzes structural load specifications and extracts structured data about design loads, load combinations, and load paths."
    
    @property
    def price(self) -> float:
        return 249.0
    
    def _get_analysis_prompt(self, text: str) -> str:
        """
        Creates a prompt for structural load analysis.
        
        Args:
            text: The text to analyze.
            
        Returns:
            The prompt to send to OpenAI.
        """
        return f"""
        Analyze the following construction document text and extract all information related to structural loads.
        Focus on:
        
        1. Design loads (dead, live, snow, wind, seismic, etc.)
        2. Load combinations and factors
        3. Deflection and serviceability criteria
        4. Building code references and requirements
        5. Special loading conditions
        6. Load path considerations
        
        Return the information as a structured JSON object with appropriate nested properties.
        Only include information that is explicitly mentioned in the text.
        
        TEXT TO ANALYZE:
        {text}
        """
