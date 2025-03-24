"""
Framing Analysis Plugin

This plugin analyzes structural framing specifications and extracts structured data.
"""
from typing import Dict, Any

from app.plugins.structural.base import StructuralPlugin
from app.plugins.registry import register_plugin


@register_plugin
class FramingAnalysisPlugin(StructuralPlugin):
    """
    Plugin for analyzing structural framing specifications.
    """
    
    @property
    def id(self) -> str:
        return "structural.framing_analysis"
    
    @property
    def name(self) -> str:
        return "Structural Framing Analysis"
    
    @property
    def description(self) -> str:
        return "Analyzes structural framing specifications and extracts structured data about columns, beams, trusses, etc."
    
    @property
    def price(self) -> float:
        return 349.0
    
    def _get_analysis_prompt(self, text: str) -> str:
        """
        Creates a prompt for structural framing analysis.
        
        Args:
            text: The text to analyze.
            
        Returns:
            The prompt to send to OpenAI.
        """
        return f"""
        Analyze the following construction document text and extract all information related to structural framing systems.
        Focus on:
        
        1. Structural steel elements (columns, beams, girders, joists)
        2. Concrete structural elements (columns, beams, slabs)
        3. Wood framing elements (studs, joists, rafters, trusses)
        4. Connection types and details
        5. Material specifications and grades
        6. Load-bearing elements and systems
        7. Lateral force resisting systems (bracing, shear walls)
        
        Return the information as a structured JSON object with appropriate nested properties.
        Only include information that is explicitly mentioned in the text.
        
        TEXT TO ANALYZE:
        {text}
        """
