from typing import Dict, Any, List
import json
import re
import openai
import os
from ...plugins.base import AnalysisPlugin
from ...plugins.registry import register_plugin

@register_plugin
class PlumbingSystemsPlugin(AnalysisPlugin):
    """Plugin for analyzing plumbing systems in construction documents."""
    
    id = "mep.plumbing_systems"
    name = "Plumbing Systems Estimator"
    version = "1.0.0"
    description = "Analyzes construction documents to extract plumbing systems details, including water supply, drainage, fixtures, and special systems."
    author = "Construction AI Platform"
    category = "mep"
    price = 199.0
    
    def __init__(self):
        super().__init__()
        self.model_name = os.getenv("DOCUMENT_ANALYSIS_MODEL", "gpt-4")
    
    async def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze construction documents for plumbing systems.
        
        Args:
            text: Document text content
            context: Additional context information
            
        Returns:
            Dictionary with extracted plumbing system information
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
            You are an expert in analyzing construction documents for plumbing systems. 
            Your task is to extract detailed information about plumbing components and systems from the provided text.
            
            Specifically, identify:
            1. Water supply systems (domestic water, hot water, recirculation)
            2. Drainage systems (sanitary, storm, grease)
            3. Plumbing fixtures (toilets, sinks, showers, etc.)
            4. Special plumbing systems (gas, medical gas, etc.)
            5. Water heating equipment
            6. Piping materials and sizes
            7. Insulation requirements
            8. Special requirements or specifications
            
            Format your response as a JSON object with the following structure:
            {
                "water_supply": {
                    "domestic_cold": {
                        "pipe_material": "pipe material",
                        "main_size": "main size",
                        "pressure": "pressure requirements",
                        "special_requirements": "any special requirements",
                        "notes": "special notes"
                    },
                    "domestic_hot": {
                        "pipe_material": "pipe material",
                        "main_size": "main size",
                        "recirculation": true/false or null,
                        "special_requirements": "any special requirements",
                        "notes": "special notes"
                    }
                },
                "drainage": {
                    "sanitary": {
                        "pipe_material": "pipe material",
                        "main_size": "main size",
                        "special_requirements": "any special requirements",
                        "notes": "special notes"
                    },
                    "storm": {
                        "pipe_material": "pipe material",
                        "main_size": "main size",
                        "special_requirements": "any special requirements",
                        "notes": "special notes"
                    },
                    "grease": {
                        "interceptor_type": "interceptor type if applicable",
                        "special_requirements": "any special requirements",
                        "notes": "special notes"
                    }
                },
                "fixtures": [
                    {
                        "type": "fixture type (toilet, sink, etc.)",
                        "description": "fixture description",
                        "manufacturer": "manufacturer if specified",
                        "model": "model if specified",
                        "quantity": quantity value or null,
                        "location": "location description",
                        "special_requirements": "any special requirements",
                        "notes": "special notes"
                    }
                ],
                "water_heating": {
                    "type": "water heater type",
                    "fuel": "fuel type",
                    "capacity": "capacity",
                    "temperature": "temperature setting if specified",
                    "quantity": quantity value or null,
                    "special_requirements": "any special requirements",
                    "notes": "special notes"
                },
                "special_systems": [
                    {
                        "type": "system type (gas, medical gas, etc.)",
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
                    "any general notes about the plumbing systems"
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
            # Default costs for different plumbing components
            costs = {
                # Water supply
                "copper": 15.0,   # Per linear foot for copper pipe
                "pex": 8.0,       # Per linear foot for PEX pipe
                "cpvc": 6.0,      # Per linear foot for CPVC pipe
                
                # Drainage
                "cast_iron": 25.0,  # Per linear foot for cast iron pipe
                "pvc": 5.0,         # Per linear foot for PVC pipe
                "abs": 6.0,         # Per linear foot for ABS pipe
                
                # Fixtures
                "toilet": 350.0,     # Per toilet
                "urinal": 400.0,     # Per urinal
                "sink": 250.0,       # Per sink
                "lavatory": 300.0,   # Per lavatory
                "shower": 500.0,     # Per shower
                "tub": 700.0,        # Per tub
                "drinking_fountain": 800.0,  # Per drinking fountain
                
                # Water heating
                "water_heater_electric": 1200.0,  # Per electric water heater
                "water_heater_gas": 1500.0,      # Per gas water heater
                "water_heater_tankless": 2000.0,  # Per tankless water heater
                
                # Special systems
                "gas_piping": 20.0,    # Per linear foot for gas piping
                "med_gas": 35.0,       # Per linear foot for medical gas piping
                
                # Default
                "general": 2000.0      # Default base cost
            }
            
            # Initialize costs
            material_cost = 0
            
            # Add water supply costs - assuming 100ft of piping for estimation
            water_supply = results.get("water_supply", {})
            if water_supply:
                # Cold water
                cold = water_supply.get("domestic_cold", {})
                if cold:
                    pipe_material = cold.get("pipe_material", "").lower()
                    pipe_cost = costs["general"]
                    if "copper" in pipe_material:
                        pipe_cost = costs["copper"]
                    elif "pex" in pipe_material:
                        pipe_cost = costs["pex"]
                    elif "cpvc" in pipe_material:
                        pipe_cost = costs["cpvc"]
                    elif "pvc" in pipe_material:
                        pipe_cost = costs["pvc"]
                    
                    # Assume 100ft for estimation
                    material_cost += pipe_cost * 100
                
                # Hot water
                hot = water_supply.get("domestic_hot", {})
                if hot:
                    pipe_material = hot.get("pipe_material", "").lower()
                    pipe_cost = costs["general"]
                    if "copper" in pipe_material:
                        pipe_cost = costs["copper"]
                    elif "pex" in pipe_material:
                        pipe_cost = costs["pex"]
                    elif "cpvc" in pipe_material:
                        pipe_cost = costs["cpvc"]
                    
                    # Assume 75ft for estimation
                    material_cost += pipe_cost * 75
                    
                    # Add recirculation cost if present
                    if hot.get("recirculation"):
                        material_cost += pipe_cost * 50  # Additional 50ft for recirc
            
            # Add drainage costs - assuming 100ft of piping for estimation
            drainage = results.get("drainage", {})
            if drainage:
                # Sanitary
                sanitary = drainage.get("sanitary", {})
                if sanitary:
                    pipe_material = sanitary.get("pipe_material", "").lower()
                    pipe_cost = costs["general"]
                    if "cast" in pipe_material and "iron" in pipe_material:
                        pipe_cost = costs["cast_iron"]
                    elif "pvc" in pipe_material:
                        pipe_cost = costs["pvc"]
                    elif "abs" in pipe_material:
                        pipe_cost = costs["abs"]
                    
                    # Assume 100ft for estimation
                    material_cost += pipe_cost * 100
                
                # Storm
                storm = drainage.get("storm", {})
                if storm:
                    pipe_material = storm.get("pipe_material", "").lower()
                    pipe_cost = costs["general"]
                    if "cast" in pipe_material and "iron" in pipe_material:
                        pipe_cost = costs["cast_iron"]
                    elif "pvc" in pipe_material:
                        pipe_cost = costs["pvc"]
                    
                    # Assume 100ft for estimation
                    material_cost += pipe_cost * 100
                
                # Grease
                grease = drainage.get("grease", {})
                if grease and grease.get("interceptor_type"):
                    material_cost += 2000  # Base cost for grease interceptor
            
            # Add fixture costs
            for fixture in results.get("fixtures", []):
                fixture_type = fixture.get("type", "").lower()
                quantity = fixture.get("quantity", 1) or 1
                
                fixture_cost = costs["general"]
                if "toilet" in fixture_type or "water closet" in fixture_type:
                    fixture_cost = costs["toilet"]
                elif "urinal" in fixture_type:
                    fixture_cost = costs["urinal"]
                elif "sink" in fixture_type:
                    fixture_cost = costs["sink"]
                elif "lavatory" in fixture_type:
                    fixture_cost = costs["lavatory"]
                elif "shower" in fixture_type:
                    fixture_cost = costs["shower"]
                elif "tub" in fixture_type or "bathtub" in fixture_type:
                    fixture_cost = costs["tub"]
                elif "drinking" in fixture_type and "fountain" in fixture_type:
                    fixture_cost = costs["drinking_fountain"]
                
                material_cost += fixture_cost * quantity
            
            # Add water heating costs
            water_heating = results.get("water_heating", {})
            if water_heating:
                heater_type = water_heating.get("type", "").lower()
                fuel = water_heating.get("fuel", "").lower()
                quantity = water_heating.get("quantity", 1) or 1
                
                heater_cost = costs["general"]
                if "tankless" in heater_type:
                    heater_cost = costs["water_heater_tankless"]
                elif "gas" in fuel:
                    heater_cost = costs["water_heater_gas"]
                elif "electric" in fuel:
                    heater_cost = costs["water_heater_electric"]
                
                material_cost += heater_cost * quantity
            
            # Add special systems costs
            for system in results.get("special_systems", []):
                system_type = system.get("type", "").lower()
                
                if "gas" in system_type and not "medical" in system_type:
                    # Assume 100ft of gas piping
                    material_cost += costs["gas_piping"] * 100
                elif "medical" in system_type and "gas" in system_type:
                    # Assume 50ft of medical gas piping
                    material_cost += costs["med_gas"] * 50
                else:
                    material_cost += costs["general"]
            
            # Estimate labor cost (typically 100-120% of material cost for plumbing)
            labor_cost = material_cost * 1.1
            
            # Create or update cost estimates
            if "cost_estimates" not in results:
                results["cost_estimates"] = {}
            
            results["cost_estimates"]["estimated_material_cost"] = round(material_cost, 2) if material_cost > 0 else None
            results["cost_estimates"]["estimated_labor_cost"] = round(labor_cost, 2) if labor_cost > 0 else None
            results["cost_estimates"]["currency"] = "USD"
        
        return results
