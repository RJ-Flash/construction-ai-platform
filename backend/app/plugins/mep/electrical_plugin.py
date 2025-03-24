from typing import Dict, Any, List
import json
import re
import openai
import os
from ...plugins.base import AnalysisPlugin
from ...plugins.registry import register_plugin

@register_plugin
class ElectricalSystemsPlugin(AnalysisPlugin):
    """Plugin for analyzing electrical systems in construction documents."""
    
    id = "mep.electrical_systems"
    name = "Electrical Systems Estimator"
    version = "1.0.0"
    description = "Analyzes construction documents to extract electrical systems details, including service, distribution, lighting, and low voltage systems."
    author = "Construction AI Platform"
    category = "mep"
    price = 199.0
    
    def __init__(self):
        super().__init__()
        self.model_name = os.getenv("DOCUMENT_ANALYSIS_MODEL", "gpt-4")
    
    async def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze construction documents for electrical systems.
        
        Args:
            text: Document text content
            context: Additional context information
            
        Returns:
            Dictionary with extracted electrical system information
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
            You are an expert in analyzing construction documents for electrical systems. 
            Your task is to extract detailed information about electrical components and systems from the provided text.
            
            Specifically, identify:
            1. Electrical service information (size, voltage, phases)
            2. Distribution systems (panels, transformers, switchgear)
            3. Lighting fixtures and controls
            4. Power outlets and special purpose receptacles
            5. Low voltage systems (communications, security, fire alarm)
            6. Emergency/backup power
            7. Special systems or equipment
            8. Relevant electrical specifications and requirements
            
            Format your response as a JSON object with the following structure:
            {
                "electrical_service": {
                    "size": "service size in amperes",
                    "voltage": "service voltage",
                    "phases": "number of phases",
                    "provider": "utility provider if mentioned",
                    "special_requirements": "any special service requirements"
                },
                "distribution": [
                    {
                        "type": "equipment type (panel, transformer, switchgear, etc.)",
                        "rating": "equipment rating",
                        "location": "equipment location",
                        "description": "additional description",
                        "quantity": quantity value or null,
                        "notes": "special notes"
                    }
                ],
                "lighting": [
                    {
                        "type": "fixture type",
                        "location": "fixture location",
                        "quantity": quantity value or null,
                        "wattage": "wattage per fixture if available",
                        "control_type": "lighting controls (switches, dimmers, etc.)",
                        "description": "additional description",
                        "notes": "special notes"
                    }
                ],
                "power": [
                    {
                        "type": "receptacle/outlet type",
                        "location": "location description",
                        "quantity": quantity value or null,
                        "circuit_type": "dedicated/standard/etc.",
                        "special_requirements": "GFCI, weatherproof, etc.",
                        "notes": "special notes"
                    }
                ],
                "low_voltage": [
                    {
                        "system_type": "system type (data, fire alarm, security, etc.)",
                        "components": ["list of components"],
                        "description": "system description",
                        "special_requirements": "any special requirements",
                        "notes": "special notes"
                    }
                ],
                "emergency_power": {
                    "type": "generator/UPS/battery/etc.",
                    "capacity": "capacity if specified",
                    "duration": "runtime if specified",
                    "coverage": "what systems are covered",
                    "notes": "special notes"
                },
                "special_systems": [
                    {
                        "type": "system type",
                        "description": "system description",
                        "special_requirements": "any special requirements",
                        "notes": "special notes"
                    }
                ],
                "cost_estimates": {
                    "estimated_material_cost": estimated material cost value or null,
                    "estimated_labor_cost": estimated labor cost value or null,
                    "currency": "USD"
                },
                "notes": [
                    "any general notes about the electrical systems"
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
            # Default costs for different electrical components
            costs = {
                # Service and distribution
                "service": 4000.0,  # Base cost for electrical service
                "panel": 1500.0,    # Per panel
                "transformer": 3000.0,  # Per transformer
                "switchgear": 10000.0,  # Per switchgear
                
                # Lighting
                "light_fixture": 200.0,  # Per standard fixture
                "led": 250.0,       # Per LED fixture
                "controls": 300.0,  # Per control system
                
                # Power
                "receptacle": 45.0,  # Per standard receptacle
                "gfci": 65.0,       # Per GFCI receptacle
                "special": 120.0,   # Per special purpose receptacle
                
                # Low voltage
                "data": 2000.0,     # Base cost for data system
                "security": 3000.0,  # Base cost for security system
                "fire_alarm": 5000.0,  # Base cost for fire alarm system
                
                # Emergency power
                "generator": 15000.0,  # Base cost for generator
                "ups": 4000.0,        # Base cost for UPS
                
                # Default
                "general": 5000.0   # Default base cost
            }
            
            # Initialize costs
            material_cost = 0
            
            # Add electrical service costs
            service = results.get("electrical_service", {})
            if service:
                material_cost += costs["service"]
                
            # Add distribution costs
            for item in results.get("distribution", []):
                item_type = item.get("type", "").lower()
                quantity = item.get("quantity", 1) or 1
                
                if "panel" in item_type:
                    material_cost += costs["panel"] * quantity
                elif "transformer" in item_type:
                    material_cost += costs["transformer"] * quantity
                elif "switchgear" in item_type:
                    material_cost += costs["switchgear"] * quantity
                else:
                    material_cost += costs["general"] * quantity
            
            # Add lighting costs
            for item in results.get("lighting", []):
                item_type = item.get("type", "").lower()
                quantity = item.get("quantity", 1) or 1
                
                if "led" in item_type:
                    material_cost += costs["led"] * quantity
                else:
                    material_cost += costs["light_fixture"] * quantity
                
                if "control" in item.get("control_type", "").lower():
                    material_cost += costs["controls"]
            
            # Add power costs
            for item in results.get("power", []):
                item_type = item.get("type", "").lower()
                quantity = item.get("quantity", 1) or 1
                
                if "gfci" in item_type or "gfci" in item.get("special_requirements", "").lower():
                    material_cost += costs["gfci"] * quantity
                elif "special" in item_type or "dedicated" in item.get("circuit_type", "").lower():
                    material_cost += costs["special"] * quantity
                else:
                    material_cost += costs["receptacle"] * quantity
            
            # Add low voltage system costs
            for item in results.get("low_voltage", []):
                system_type = item.get("system_type", "").lower()
                
                if "data" in system_type or "network" in system_type:
                    material_cost += costs["data"]
                elif "security" in system_type:
                    material_cost += costs["security"]
                elif "fire" in system_type and "alarm" in system_type:
                    material_cost += costs["fire_alarm"]
                else:
                    material_cost += costs["general"]
            
            # Add emergency power costs
            emergency = results.get("emergency_power", {})
            if emergency:
                emergency_type = emergency.get("type", "").lower()
                if "generator" in emergency_type:
                    material_cost += costs["generator"]
                elif "ups" in emergency_type:
                    material_cost += costs["ups"]
                else:
                    material_cost += costs["general"]
            
            # Add special systems costs
            for item in results.get("special_systems", []):
                material_cost += costs["general"]
            
            # Estimate labor cost (typically 60-70% of material cost for electrical)
            labor_cost = material_cost * 0.7
            
            # Create or update cost estimates
            if "cost_estimates" not in results:
                results["cost_estimates"] = {}
            
            results["cost_estimates"]["estimated_material_cost"] = round(material_cost, 2) if material_cost > 0 else None
            results["cost_estimates"]["estimated_labor_cost"] = round(labor_cost, 2) if labor_cost > 0 else None
            results["cost_estimates"]["currency"] = "USD"
        
        return results
