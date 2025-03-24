from typing import Dict, Any, List
import json
import re
import openai
import os
from ...plugins.base import AnalysisPlugin
from ...plugins.registry import register_plugin

@register_plugin
class WallsPartitionsPlugin(AnalysisPlugin):
    """Plugin for analyzing walls and partitions in construction documents."""
    
    id = "architectural.walls_partitions"
    name = "Walls and Partitions Estimator"
    version = "1.0.0"
    description = "Analyzes construction documents to extract walls and partitions details, including types, materials, dimensions, and quantities."
    author = "Construction AI Platform"
    category = "architectural"
    price = 99.0
    
    def __init__(self):
        super().__init__()
        self.model_name = os.getenv("DOCUMENT_ANALYSIS_MODEL", "gpt-4")
    
    async def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze construction documents for walls and partitions.
        
        Args:
            text: Document text content
            context: Additional context information
            
        Returns:
            Dictionary with extracted wall and partition information
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
            You are an expert in analyzing construction documents for walls and partitions. 
            Your task is to extract detailed information about walls and partitions from the provided text.
            
            Specifically, identify:
            1. Wall types (e.g., exterior walls, interior partitions, fire walls, load-bearing walls)
            2. Wall materials (e.g., concrete, masonry, wood stud, metal stud)
            3. Wall dimensions (thickness, height, length if available)
            4. Finishes (e.g., drywall, plaster, paneling)
            5. Insulation requirements
            6. Fire ratings
            7. Acoustic ratings
            8. Special details or requirements
            
            Format your response as a JSON object with the following structure:
            {
                "walls": [
                    {
                        "type": "wall type",
                        "subtype": "wall subtype (if applicable)",
                        "material": "primary material",
                        "thickness": "wall thickness",
                        "height": "wall height (if specified)",
                        "length": "wall length (if specified)",
                        "finish": "wall finish",
                        "insulation": "insulation details",
                        "fire_rating": "fire rating (if specified)",
                        "acoustic_rating": "acoustic rating (if specified)",
                        "special_requirements": "any special details",
                        "location": "location description if available",
                        "quantity": quantity value or null,
                        "unit": "measurement unit (e.g., SF, LF)"
                    }
                ],
                "partitions": [
                    {
                        "type": "partition type",
                        "material": "primary material",
                        "thickness": "partition thickness",
                        "height": "partition height (if specified)",
                        "finish": "partition finish",
                        "fire_rating": "fire rating (if specified)",
                        "acoustic_rating": "acoustic rating (if specified)",
                        "special_requirements": "any special details",
                        "location": "location description if available",
                        "quantity": quantity value or null,
                        "unit": "measurement unit (e.g., SF, LF)"
                    }
                ],
                "cost_estimates": {
                    "walls_total_area": estimated total area value or null,
                    "walls_unit": "SF or appropriate unit",
                    "partitions_total_area": estimated total area value or null,
                    "partitions_unit": "SF or appropriate unit",
                    "estimated_material_cost": estimated material cost value or null,
                    "estimated_labor_cost": estimated labor cost value or null,
                    "currency": "USD"
                },
                "notes": [
                    "any general notes about the walls and partitions"
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
        if "error" in results or not results.get("walls"):
            return results
        
        # If cost estimates aren't provided, try to calculate them
        if "cost_estimates" not in results or not results["cost_estimates"].get("estimated_material_cost"):
            # Default costs per square foot for different wall types
            costs = {
                "concrete": 22.0,
                "masonry": 18.5,
                "wood stud": 12.0,
                "metal stud": 14.5,
                "drywall": 2.5,
                "plaster": 5.0,
                "general": 15.0  # Default
            }
            
            # Calculate total wall area
            total_area = 0
            for wall in results.get("walls", []):
                if wall.get("quantity"):
                    total_area += wall.get("quantity", 0)
                elif wall.get("length") and wall.get("height"):
                    # Try to parse length and height as numbers
                    try:
                        length = float(re.search(r'(\d+(\.\d+)?)', wall.get("length", "0")).group(1))
                        height = float(re.search(r'(\d+(\.\d+)?)', wall.get("height", "0")).group(1))
                        total_area += length * height
                    except (AttributeError, ValueError):
                        # If parsing fails, skip this wall
                        pass
            
            # Calculate total partition area
            partition_area = 0
            for partition in results.get("partitions", []):
                if partition.get("quantity"):
                    partition_area += partition.get("quantity", 0)
                elif partition.get("length") and partition.get("height"):
                    # Try to parse length and height as numbers
                    try:
                        length = float(re.search(r'(\d+(\.\d+)?)', partition.get("length", "0")).group(1))
                        height = float(re.search(r'(\d+(\.\d+)?)', partition.get("height", "0")).group(1))
                        partition_area += length * height
                    except (AttributeError, ValueError):
                        # If parsing fails, skip this partition
                        pass
            
            # Estimate costs
            material_cost = 0
            for wall in results.get("walls", []):
                area = wall.get("quantity", 0)
                # Try to determine material type and use appropriate cost
                material = wall.get("material", "").lower()
                cost_per_sf = costs.get("general")  # Default
                for material_type, cost in costs.items():
                    if material_type in material:
                        cost_per_sf = cost
                        break
                material_cost += area * cost_per_sf
            
            # Add partition costs
            for partition in results.get("partitions", []):
                area = partition.get("quantity", 0)
                # Try to determine material type and use appropriate cost
                material = partition.get("material", "").lower()
                cost_per_sf = costs.get("general")  # Default
                for material_type, cost in costs.items():
                    if material_type in material:
                        cost_per_sf = cost
                        break
                material_cost += area * cost_per_sf
            
            # Estimate labor cost (typically 60-70% of material cost in construction)
            labor_cost = material_cost * 0.65
            
            # Create or update cost estimates
            if "cost_estimates" not in results:
                results["cost_estimates"] = {}
            
            results["cost_estimates"]["walls_total_area"] = total_area
            results["cost_estimates"]["walls_unit"] = "SF"
            results["cost_estimates"]["partitions_total_area"] = partition_area
            results["cost_estimates"]["partitions_unit"] = "SF"
            results["cost_estimates"]["estimated_material_cost"] = round(material_cost, 2) if material_cost > 0 else None
            results["cost_estimates"]["estimated_labor_cost"] = round(labor_cost, 2) if labor_cost > 0 else None
            results["cost_estimates"]["currency"] = "USD"
        
        return results