from typing import Dict, Any, List
import json
import re
import openai
import os
from ...plugins.base import AnalysisPlugin
from ...plugins.registry import register_plugin

@register_plugin
class HVACSystemsPlugin(AnalysisPlugin):
    """Plugin for analyzing HVAC systems in construction documents."""
    
    id = "mep.hvac_systems"
    name = "HVAC & Mechanical Estimator"
    version = "1.0.0"
    description = "Analyzes construction documents to extract HVAC and mechanical systems details, including heating, cooling, ventilation, and controls."
    author = "Construction AI Platform"
    category = "mep"
    price = 249.0
    
    def __init__(self):
        super().__init__()
        self.model_name = os.getenv("DOCUMENT_ANALYSIS_MODEL", "gpt-4")
    
    async def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze construction documents for HVAC and mechanical systems.
        
        Args:
            text: Document text content
            context: Additional context information
            
        Returns:
            Dictionary with extracted HVAC system information
        """
        if not self.validate_input(text):
            return {"error": "Invalid input text for analysis"}
        
        # Get available prompts
        prompts = self.get_prompts()
        system_prompt = prompts["system_prompt"]
        
        # Call OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text[:4000]}  # Limit text size
                ],
                temperature=0.1,  # Low temperature for consistent results
                max_tokens=2000
            )
            
            # Extract and parse response
            ai_response = response.choices[0].message.content
            try:
                result = json.loads(ai_response)
                return result
            except json.JSONDecodeError:
                # If response is not valid JSON, try to extract it
                json_match = re.search(r'```json\n(.*?)\n```', ai_response, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group(1))
                    return result
                    
                # If still can't parse, return raw response
                return {
                    "error": "Could not parse AI response as JSON",
                    "raw_response": ai_response
                }
                
        except Exception as e:
            return {
                "error": f"Error analyzing document: {str(e)}"
            }
    
    def get_prompts(self) -> Dict[str, str]:
        """
        Get the prompts used by this plugin.
        
        Returns:
            Dictionary of prompt templates
        """
        return {
            "system_prompt": """
            You are an expert in analyzing construction documents for HVAC and mechanical systems. 
            Your task is to extract detailed information about HVAC components and systems from the provided text.
            
            Specifically, identify:
            1. Heating systems (boilers, furnaces, heat pumps, etc.)
            2. Cooling systems (chillers, condensers, cooling towers, etc.)
            3. Air handling units and distribution systems
            4. Ventilation systems
            5. Ductwork types and sizes
            6. Mechanical equipment and specifications
            7. Controls and building automation
            8. Energy efficiency features
            9. Load calculations if mentioned
            
            Format your response as a JSON object with the following structure:
            {
                "heating_systems": [
                    {
                        "type": "equipment type (boiler, furnace, etc.)",
                        "fuel": "fuel type",
                        "capacity": "heating capacity",
                        "efficiency": "efficiency rating if specified",
                        "manufacturer": "manufacturer if specified",
                        "model": "model if specified",
                        "quantity": quantity value or null,
                        "location": "equipment location",
                        "special_requirements": "any special requirements",
                        "notes": "special notes"
                    }
                ],
                "cooling_systems": [
                    {
                        "type": "equipment type (chiller, DX, etc.)",
                        "capacity": "cooling capacity",
                        "efficiency": "efficiency rating if specified",
                        "refrigerant": "refrigerant type",
                        "manufacturer": "manufacturer if specified",
                        "model": "model if specified",
                        "quantity": quantity value or null,
                        "location": "equipment location",
                        "special_requirements": "any special requirements",
                        "notes": "special notes"
                    }
                ],
                "air_handling": [
                    {
                        "type": "unit type (AHU, RTU, etc.)",
                        "capacity": "capacity",
                        "cfm": "air flow rate",
                        "static_pressure": "static pressure",
                        "manufacturer": "manufacturer if specified",
                        "model": "model if specified",
                        "quantity": quantity value or null,
                        "location": "unit location",
                        "special_requirements": "any special requirements",
                        "notes": "special notes"
                    }
                ],
                "ventilation": [
                    {
                        "type": "system type (exhaust, supply, etc.)",
                        "cfm": "air flow rate",
                        "areas_served": "areas served",
                        "special_requirements": "any special requirements",
                        "notes": "special notes"
                    }
                ],
                "ductwork": {
                    "material": "duct material",
                    "insulation": "insulation requirements",
                    "special_requirements": "any special requirements",
                    "notes": "special notes"
                },
                "controls": {
                    "type": "control system type",
                    "protocol": "communication protocol",
                    "special_requirements": "any special requirements",
                    "notes": "special notes"
                },
                "energy_efficiency": [
                    {
                        "feature": "efficiency feature",
                        "description": "description",
                        "benefits": "benefits",
                        "notes": "special notes"
                    }
                ],
                "load_calculations": {
                    "heating_load": "heating load value",
                    "cooling_load": "cooling load value",
                    "notes": "calculation notes"
                },
                "cost_estimates": {
                    "estimated_material_cost": estimated material cost value or null,
                    "estimated_labor_cost": estimated labor cost value or null,
                    "currency": "USD"
                },
                "notes": [
                    "any general notes about the HVAC systems"
                ]
            }
            
            Only include information that is explicitly stated in the document. 
            If information is not available, use null values.
            """
        }
    
    def format_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the analysis results, including estimating costs if not provided.
        
        Args:
            results: Raw analysis results
            
        Returns:
            Formatted results with additional cost information if applicable
        """
        # Check if we have valid results
        if "error" in results:
            return results
        
        # If cost estimates aren't provided, try to calculate them
        if "cost_estimates" not in results or not results["cost_estimates"].get("estimated_material_cost"):
            # Default costs for different HVAC components
            costs = {
                # Heating systems
                "boiler_small": 5000.0,    # Small boiler (<500 MBH)
                "boiler_medium": 15000.0,  # Medium boiler (500-1500 MBH)
                "boiler_large": 30000.0,   # Large boiler (>1500 MBH)
                "furnace": 3000.0,         # Standard furnace
                "heat_pump": 7000.0,       # Heat pump
                
                # Cooling systems
                "chiller_small": 20000.0,   # Small chiller (<100 tons)
                "chiller_medium": 50000.0,  # Medium chiller (100-300 tons)
                "chiller_large": 100000.0,  # Large chiller (>300 tons)
                "dx_system": 10000.0,       # DX cooling system
                "cooling_tower_small": 15000.0,  # Small cooling tower
                "cooling_tower_large": 40000.0,  # Large cooling tower
                
                # Air handling units
                "ahu_small": 8000.0,     # Small AHU (<5,000 CFM)
                "ahu_medium": 20000.0,   # Medium AHU (5,000-15,000 CFM)
                "ahu_large": 40000.0,    # Large AHU (>15,000 CFM)
                "rtu_small": 15000.0,    # Small RTU
                "rtu_medium": 30000.0,   # Medium RTU
                "rtu_large": 60000.0,    # Large RTU
                
                # Ventilation
                "exhaust_fan_small": 1000.0,   # Small exhaust fan
                "exhaust_fan_large": 3000.0,   # Large exhaust fan
                "energy_recovery": 10000.0,    # Energy recovery ventilator
                
                # Ductwork (per square foot of building area)
                "ductwork": 10.0,     # Per square foot
                
                # Controls
                "basic_controls": 5000.0,    # Basic controls
                "bms": 20000.0,              # Building Management System
                
                # Default
                "general": 5000.0            # Default base cost
            }
            
            # Initialize costs
            material_cost = 0
            
            # Add heating system costs
            for item in results.get("heating_systems", []):
                item_type = item.get("type", "").lower()
                capacity_str = item.get("capacity", "").lower()
                quantity = item.get("quantity", 1) or 1
                
                # Try to parse capacity
                capacity_value = 0
                try:
                    # Extract numeric value from capacity string
                    capacity_match = re.search(r'(\d+(?:\.\d+)?)', capacity_str)
                    if capacity_match:
                        capacity_value = float(capacity_match.group(1))
                except (ValueError, AttributeError):
                    capacity_value = 0
                
                # Determine equipment cost based on type and capacity
                equipment_cost = costs["general"]
                if "boiler" in item_type:
                    if capacity_value < 500 or "small" in capacity_str:
                        equipment_cost = costs["boiler_small"]
                    elif capacity_value < 1500 or "medium" in capacity_str:
                        equipment_cost = costs["boiler_medium"]
                    else:
                        equipment_cost = costs["boiler_large"]
                elif "furnace" in item_type:
                    equipment_cost = costs["furnace"]
                elif "heat" in item_type and "pump" in item_type:
                    equipment_cost = costs["heat_pump"]
                
                material_cost += equipment_cost * quantity
            
            # Add cooling system costs
            for item in results.get("cooling_systems", []):
                item_type = item.get("type", "").lower()
                capacity_str = item.get("capacity", "").lower()
                quantity = item.get("quantity", 1) or 1
                
                # Try to parse capacity
                capacity_value = 0
                try:
                    # Extract numeric value from capacity string
                    capacity_match = re.search(r'(\d+(?:\.\d+)?)', capacity_str)
                    if capacity_match:
                        capacity_value = float(capacity_match.group(1))
                except (ValueError, AttributeError):
                    capacity_value = 0
                
                # Determine equipment cost based on type and capacity
                equipment_cost = costs["general"]
                if "chiller" in item_type:
                    if capacity_value < 100 or "small" in capacity_str:
                        equipment_cost = costs["chiller_small"]
                    elif capacity_value < 300 or "medium" in capacity_str:
                        equipment_cost = costs["chiller_medium"]
                    else:
                        equipment_cost = costs["chiller_large"]
                elif "dx" in item_type:
                    equipment_cost = costs["dx_system"]
                elif "cooling" in item_type and "tower" in item_type:
                    if capacity_value < 300 or "small" in capacity_str:
                        equipment_cost = costs["cooling_tower_small"]
                    else:
                        equipment_cost = costs["cooling_tower_large"]
                
                material_cost += equipment_cost * quantity
            
            # Add air handling unit costs
            for item in results.get("air_handling", []):
                item_type = item.get("type", "").lower()
                cfm_str = item.get("cfm", "").lower()
                quantity = item.get("quantity", 1) or 1
                
                # Try to parse CFM
                cfm_value = 0
                try:
                    # Extract numeric value from CFM string
                    cfm_match = re.search(r'(\d+(?:\.\d+)?)', cfm_str)
                    if cfm_match:
                        cfm_value = float(cfm_match.group(1))
                except (ValueError, AttributeError):
                    cfm_value = 0
                
                # Determine equipment cost based on type and CFM
                equipment_cost = costs["general"]
                if "ahu" in item_type or "air" in item_type and "handler" in item_type:
                    if cfm_value < 5000 or "small" in cfm_str:
                        equipment_cost = costs["ahu_small"]
                    elif cfm_value < 15000 or "medium" in cfm_str:
                        equipment_cost = costs["ahu_medium"]
                    else:
                        equipment_cost = costs["ahu_large"]
                elif "rtu" in item_type or "roof" in item_type and "top" in item_type:
                    if cfm_value < 5000 or "small" in cfm_str:
                        equipment_cost = costs["rtu_small"]
                    elif cfm_value < 15000 or "medium" in cfm_str:
                        equipment_cost = costs["rtu_medium"]
                    else:
                        equipment_cost = costs["rtu_large"]
                
                material_cost += equipment_cost * quantity
            
            # Add ventilation system costs
            for item in results.get("ventilation", []):
                item_type = item.get("type", "").lower()
                cfm_str = item.get("cfm", "").lower()
                
                # Try to parse CFM
                cfm_value = 0
                try:
                    # Extract numeric value from CFM string
                    cfm_match = re.search(r'(\d+(?:\.\d+)?)', cfm_str)
                    if cfm_match:
                        cfm_value = float(cfm_match.group(1))
                except (ValueError, AttributeError):
                    cfm_value = 0
                
                # Determine equipment cost based on type and CFM
                equipment_cost = costs["general"]
                if "exhaust" in item_type or "fan" in item_type:
                    if cfm_value < 2000 or "small" in cfm_str:
                        equipment_cost = costs["exhaust_fan_small"]
                    else:
                        equipment_cost = costs["exhaust_fan_large"]
                elif "energy" in item_type and ("recovery" in item_type or "erv" in item_type):
                    equipment_cost = costs["energy_recovery"]
                
                material_cost += equipment_cost
            
            # Add ductwork costs - assume 10,000 SF building for estimation
            ductwork = results.get("ductwork", {})
            if ductwork:
                material_cost += costs["ductwork"] * 10000  # Assume 10,000 SF building
            
            # Add controls costs
            controls = results.get("controls", {})
            if controls:
                control_type = controls.get("type", "").lower()
                if "bms" in control_type or "building" in control_type and "management" in control_type:
                    material_cost += costs["bms"]
                else:
                    material_cost += costs["basic_controls"]
            
            # Estimate labor cost (typically 80-100% of material cost for HVAC)
            labor_cost = material_cost * 0.9
            
            # Create or update cost estimates
            if "cost_estimates" not in results:
                results["cost_estimates"] = {}
            
            results["cost_estimates"]["estimated_material_cost"] = round(material_cost, 2) if material_cost > 0 else None
            results["cost_estimates"]["estimated_labor_cost"] = round(labor_cost, 2) if labor_cost > 0 else None
            results["cost_estimates"]["currency"] = "USD"
        
        return results
