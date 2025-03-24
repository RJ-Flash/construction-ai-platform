"""
Labor Cost Plugin

This plugin analyzes specifications and extracts labor cost data.
"""
from typing import Dict, Any

from app.plugins.cost.base import CostPlugin
from app.plugins.registry import register_plugin


@register_plugin
class LaborCostPlugin(CostPlugin):
    """
    Plugin for analyzing and estimating labor costs.
    """
    
    @property
    def id(self) -> str:
        return "cost.labor_cost"
    
    @property
    def name(self) -> str:
        return "Labor Cost Estimator"
    
    @property
    def description(self) -> str:
        return "Analyzes specifications and estimates labor costs for construction projects."
    
    @property
    def price(self) -> float:
        return 399.0
    
    def _get_analysis_prompt(self, text: str) -> str:
        """
        Creates a prompt for labor cost analysis.
        
        Args:
            text: The text to analyze.
            
        Returns:
            The prompt to send to OpenAI.
        """
        return f"""
        Analyze the following construction document text and extract all information related to labor requirements and associated costs.
        Focus on:
        
        1. Labor categories (carpenters, electricians, plumbers, etc.)
        2. Labor hours or person-days required
        3. Labor rates (if provided)
        4. Specialized labor requirements
        5. Scheduling and sequencing considerations
        6. Productivity factors or assumptions
        
        For labor rates not explicitly stated in the text, provide reasonable market rate estimates in USD per hour.
        
        Return the information as a structured JSON object with these properties:
        - labor_categories: An array of labor category objects, each containing:
          - category: Labor category/type
          - description: Detailed description of work
          - hours_required: Estimated labor hours
          - hourly_rate: Cost per hour in USD
          - total_cost: Total cost for this labor category in USD
        - summary: Object containing:
          - total_labor_cost: Sum of all labor costs
          - total_labor_hours: Sum of all labor hours
          - average_hourly_rate: Average hourly rate across all categories
          - confidence_level: High/Medium/Low based on information quality
          - notes: Any important notes about the estimates
        
        Only include information that is explicitly mentioned or can be reasonably inferred from the text.
        
        TEXT TO ANALYZE:
        {text}
        """
