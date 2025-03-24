"""
Material Cost Plugin

This plugin analyzes specifications and extracts material cost data.
"""
from typing import Dict, Any

from app.plugins.cost.base import CostPlugin
from app.plugins.registry import register_plugin


@register_plugin
class MaterialCostPlugin(CostPlugin):
    """
    Plugin for analyzing and estimating material costs.
    """
    
    @property
    def id(self) -> str:
        return "cost.material_cost"
    
    @property
    def name(self) -> str:
        return "Material Cost Estimator"
    
    @property
    def description(self) -> str:
        return "Analyzes specifications and estimates material costs for construction projects."
    
    @property
    def price(self) -> float:
        return 399.0
    
    def _get_analysis_prompt(self, text: str) -> str:
        """
        Creates a prompt for material cost analysis.
        
        Args:
            text: The text to analyze.
            
        Returns:
            The prompt to send to OpenAI.
        """
        return f"""
        Analyze the following construction document text and extract all information related to construction materials and their costs.
        Focus on:
        
        1. Material types and specifications
        2. Quantities and units
        3. Unit costs (if provided)
        4. Material grades and quality levels
        5. Special material requirements
        6. Market price considerations
        
        For materials without explicit costs in the text, provide reasonable market rate estimates in USD.
        
        Return the information as a structured JSON object with these properties:
        - materials: An array of material objects, each containing:
          - name: Material name/type
          - description: Detailed description
          - quantity: Estimated quantity
          - unit: Unit of measurement
          - unit_cost: Cost per unit in USD
          - total_cost: Total cost for this material in USD
        - summary: Object containing:
          - total_material_cost: Sum of all material costs
          - confidence_level: High/Medium/Low based on information quality
          - notes: Any important notes about the estimates
        
        Only include information that is explicitly mentioned or can be reasonably inferred from the text.
        
        TEXT TO ANALYZE:
        {text}
        """
