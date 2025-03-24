"""
Takeoff Plugin

This plugin analyzes drawings and specifications to generate quantity takeoffs.
"""
from typing import Dict, Any

from app.plugins.cost.base import CostPlugin
from app.plugins.registry import register_plugin


@register_plugin
class TakeoffPlugin(CostPlugin):
    """
    Plugin for generating quantity takeoffs from construction documents.
    """
    
    @property
    def id(self) -> str:
        return "cost.takeoff"
    
    @property
    def name(self) -> str:
        return "Quantity Takeoff Generator"
    
    @property
    def description(self) -> str:
        return "Analyzes construction documents to extract quantities of materials and components for cost estimation."
    
    @property
    def price(self) -> float:
        return 499.0
    
    def _get_analysis_prompt(self, text: str) -> str:
        """
        Creates a prompt for quantity takeoff analysis.
        
        Args:
            text: The text to analyze.
            
        Returns:
            The prompt to send to OpenAI.
        """
        return f"""
        Analyze the following construction document text and generate a detailed quantity takeoff.
        Focus on:
        
        1. Identifying all materials, components, and systems
        2. Determining quantities with appropriate units
        3. Organizing by CSI MasterFormat divisions
        4. Including both rough and finished materials
        5. Accounting for waste factors
        6. Identifying areas needing further clarification
        
        Return the information as a structured JSON object with these properties:
        - divisions: An array of division objects, each containing:
          - number: CSI MasterFormat division number
          - name: Division name
          - items: Array of item objects, each containing:
            - description: Detailed description
            - quantity: Numeric quantity
            - unit: Unit of measurement
            - notes: Any relevant notes about the item
        - summary: Object containing:
          - total_items: Total number of line items
          - confidence_level: High/Medium/Low based on information quality
          - incomplete_areas: Array of areas needing more information
          - notes: Any important notes about the takeoff
        
        Only include information that is explicitly mentioned or can be reasonably inferred from the text.
        
        TEXT TO ANALYZE:
        {text}
        """
