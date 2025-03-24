"""
Foundation Analysis Plugin

This plugin analyzes foundation specifications and extracts structured data.
"""
from typing import Dict, Any

from app.plugins.structural.base import StructuralPlugin
from app.plugins.registry import register_plugin


@register_plugin
class FoundationAnalysisPlugin(StructuralPlugin):
    """
    Plugin for analyzing foundation systems specifications.
    """
    
    @property
    def id(self) -> str:
        return "structural.foundation_analysis"
    
    @property
    def name(self) -> str:
        return "Foundation Analysis"
    
    @property
    def description(self) -> str:
        return "Analyzes foundation specifications and extracts structured data about foundation systems."
    
    @property
    def price(self) -> float:
        return 299.0
    
    def _get_analysis_prompt(self, text: str) -> str:
        """
        Creates a prompt for foundation analysis.
        
        Args:
            text: The text to analyze.
            
        Returns:
            The prompt to send to OpenAI.
        """
        return f"""
        Analyze the following construction document text and extract all information related to foundation systems.
        Focus on:
        
        1. Foundation types (slab-on-grade, mat, spread footings, piles, etc.)
        2. Concrete specifications (strength, mix design, reinforcement)
        3. Dimensions and depths
        4. Soil bearing capacity and assumptions
        5. Waterproofing and drainage systems
        6. Special foundation elements (grade beams, pile caps, etc.)
        
        Return the information as a structured JSON object with appropriate nested properties.
        Only include information that is explicitly mentioned in the text.
        
        TEXT TO ANALYZE:
        {text}
        """
