from typing import Dict, Any, List
import json
import re
import openai
import os
from ...plugins.base import AnalysisPlugin
from ...plugins.registry import register_plugin

@register_plugin
class ConcreteStructuresPlugin(AnalysisPlugin):
    """Plugin for analyzing concrete structures in construction documents."""
    
    id = "structural.concrete"
    name = "Concrete Structures Plugin"
    version = "1.0.0"
    description = "Analyzes construction documents to extract concrete structural elements, reinforcement details, specifications, and quantities."
    author = "Construction AI Platform"
    category = "structural"
    price = 199.0
    
    def __init__(self):
        super().__init__()
        self.model_name = os.getenv("DOCUMENT_ANALYSIS_MODEL", "gpt-4")
    
    async def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze construction documents for concrete structures.
        
        Args:
            text: Document text content
            context: Additional context information
            
        Returns:
            Dictionary with extracted concrete structure information
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
            You are an expert structural engineer specializing in concrete structures.
            Your task is to analyze construction documents and extract detailed information about concrete structural elements.
            
            Specifically, identify:
            1. Concrete elements (foundations, footings, slabs, columns, beams, walls, etc.)
            2. Concrete specifications (strength, class, mix design)
            3. Reinforcement details (rebar size, spacing, placement)
            4. Dimensions and quantities
            5. Special requirements (water/cement ratio, admixtures, curing requirements)
            
            Format your response as a JSON object with the following structure:
            {
                "foundations": [
                    {
                        "type": "foundation type (strip, spread, raft, etc.)",
                        "dimensions": "dimensions",
                        "concrete_class": "concrete class/strength",
                        "reinforcement": "reinforcement details",
                        "depth": "depth/thickness",
                        "location": "location description",
                        "special_requirements": "special requirements",
                        "quantity": quantity value or null,
                        "unit": "measurement unit (e.g., CY, CF)"
                    }
                ],
                "columns": [
                    {
                        "type": "column type",
                        "dimensions": "dimensions",
                        "concrete_class": "concrete class/strength",
                        "reinforcement": "reinforcement details",
                        "height": "height",
                        "location": "location description",
                        "special_requirements": "special requirements",
                        "quantity": quantity value or null,
                        "unit": "measurement unit (e.g., CY, CF)"
                    }
                ],
                "beams": [
                    {
                        "type": "beam type",
                        "dimensions": "dimensions",
                        "concrete_class": "concrete class/strength",
                        "reinforcement": "reinforcement details",
                        "span": "span",
                        "location": "location description",
                        "special_requirements": "special requirements",
                        "quantity": quantity value or null,
                        "unit": "measurement unit (e.g., CY, CF)"
                    }
                ],
                "slabs": [
                    {
                        "type": "slab type (on grade, suspended, etc.)",
                        "thickness": "thickness",
                        "concrete_class": "concrete class/strength",
                        "reinforcement": "reinforcement details",
                        "area": "area",
                        "location": "location description",
                        "special_requirements": "special requirements",
                        "quantity": quantity value or null,
                        "unit": "measurement unit (e.g., CY, SF)"
                    }
                ],
                "walls": [
                    {
                        "type": "wall type (shear, retaining, etc.)",
                        "thickness": "thickness",
                        "height": "height",
                        "length": "length",
                        "concrete_class": "concrete class/strength",
                        "reinforcement": "reinforcement details",
                        "location": "location description",
                        "special_requirements": "special requirements",
                        "quantity": quantity value or null,
                        "unit": "measurement unit (e.g., CY, SF)"
                    }
                ],
                "concrete_specifications": {
                    "classes": [
                        {
                            "designation": "concrete class designation",
                            "strength": "compressive strength",
                            "w_c_ratio": "water-cement ratio",
                            "cement_type": "cement type",
                            "aggregates": "aggregate specifications",
                            "admixtures": "admixtures",
                            "special_requirements": "special requirements"
                        }
                    ],
                    "curing": "curing requirements",
                    "testing": "testing requirements",
                    "general_notes": "general concrete specifications"
                },
                "reinforcement_specifications": {
                    "rebar_grades": "rebar grades used",
                    "coating": "coating requirements",
                    "splice_requirements": "splicing requirements",
                    "cover_requirements": "concrete cover requirements",
                    "general_notes": "general reinforcement specifications"
                },
                "quantity_summary": {
                    "total_concrete_volume": total concrete volume or null,
                    "total_concrete_unit": "CY or appropriate unit",
                    "total_reinforcement_weight": total reinforcement weight or null,
                    "total_reinforcement_unit": "tons or appropriate unit"
                },
                "cost_estimates": {
                    "estimated_concrete_cost": estimated concrete cost value or null,
                    "estimated_reinforcement_cost": estimated reinforcement cost value or null,
                    "estimated_formwork_cost": estimated formwork cost value or null,
                    "estimated_labor_cost": estimated labor cost value or null,
                    "currency": "USD"
                },
                "notes": [
                    "any general notes about concrete structures"
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
        if "cost_estimates" not in results or not results["cost_estimates"].get("estimated_concrete_cost"):
            # Default unit costs for concrete construction
            unit_costs = {
                "concrete": {
                    "3000": 150.0,  # $150 per cubic yard for 3000 psi
                    "4000": 175.0,  # $175 per cubic yard for 4000 psi
                    "5000": 200.0,  # $200 per cubic yard for 5000 psi
                    "6000": 225.0,  # $225 per cubic yard for 6000 psi
                    "general": 175.0  # Default
                },
                "reinforcement": 1200.0,  # $1,200 per ton
                "formwork": {
                    "foundation": 15.0,  # $15 per square foot
                    "walls": 20.0,     # $20 per square foot
                    "columns": 25.0,   # $25 per square foot
                    "elevated_slab": 18.0,  # $18 per square foot
                    "beams": 22.0,     # $22 per square foot
                    "general": 20.0    # Default
                }
            }
            
            # Calculate total concrete volume
            total_volume = 0
            
            # Collect all elements with quantities
            all_elements = []
            all_elements.extend(results.get("foundations", []))
            all_elements.extend(results.get("columns", []))
            all_elements.extend(results.get("beams", []))
            all_elements.extend(results.get("slabs", []))
            all_elements.extend(results.get("walls", []))
            
            # Calculate total concrete volume
            for element in all_elements:
                if element.get("quantity") and element.get("unit", "").upper() in ["CY", "CF"]:
                    quantity = element.get("quantity", 0)
                    # Convert from cubic feet to cubic yards if needed
                    if element.get("unit", "").upper() == "CF":
                        quantity /= 27
                    total_volume += quantity
            
            # Use volume summary if elements don't have individual quantities
            if total_volume == 0 and results.get("quantity_summary", {}).get("total_concrete_volume"):
                total_volume = results["quantity_summary"]["total_concrete_volume"]
                # Convert from cubic feet to cubic yards if needed
                if results["quantity_summary"].get("total_concrete_unit", "").upper() == "CF":
                    total_volume /= 27
            
            # Estimate concrete cost
            concrete_cost = 0
            if total_volume > 0:
                # Try to determine concrete strength/class
                avg_strength = "general"  # Default
                
                # Look at concrete specifications
                if results.get("concrete_specifications", {}).get("classes"):
                    for concrete_class in results["concrete_specifications"]["classes"]:
                        strength = concrete_class.get("strength", "")
                        match = re.search(r'(\d+)\s*(?:psi|PSI)', strength)
                        if match:
                            psi = match.group(1)
                            # Find the closest standard strength
                            for std_psi in ["3000", "4000", "5000", "6000"]:
                                if abs(int(psi) - int(std_psi)) < 500:
                                    avg_strength = std_psi
                                    break
                
                # Calculate concrete cost
                concrete_cost = total_volume * unit_costs["concrete"][avg_strength]
            
            # Estimate reinforcement cost
            reinforcement_cost = 0
            rebar_weight = results.get("quantity_summary", {}).get("total_reinforcement_weight", 0)
            
            if rebar_weight > 0:
                # Convert from pounds to tons if needed
                if results.get("quantity_summary", {}).get("total_reinforcement_unit", "").lower() == "lbs":
                    rebar_weight /= 2000
                
                reinforcement_cost = rebar_weight * unit_costs["reinforcement"]
            else:
                # Estimate based on concrete volume if weight not provided
                # Typical reinforcement ratio is about 100-150 lbs per cubic yard
                reinforcement_cost = total_volume * 125 / 2000 * unit_costs["reinforcement"]
            
            # Estimate formwork cost
            formwork_cost = 0
            
            # Estimate formwork based on element types
            for element_type, elements in results.items():
                if element_type not in ["foundations", "columns", "beams", "slabs", "walls"]:
                    continue
                
                for element in elements:
                    # Skip if no dimensions
                    if not element.get("dimensions"):
                        continue
                    
                    # Estimate formwork area based on element type
                    area = 0
                    if element_type == "foundations":
                        # For foundations, estimate as perimeter * depth
                        try:
                            match = re.search(r'(\d+(\.\d+)?)', element.get("dimensions", "0"))
                            size = float(match.group(1)) if match else 0
                            depth_match = re.search(r'(\d+(\.\d+)?)', element.get("depth", "0"))
                            depth = float(depth_match.group(1)) if depth_match else 0
                            area = size * 4 * depth  # Assuming square footprint
                        except (ValueError, AttributeError):
                            pass
                    elif element_type == "walls":
                        # For walls, use length * height * 2 (both sides)
                        try:
                            length_match = re.search(r'(\d+(\.\d+)?)', element.get("length", "0"))
                            length = float(length_match.group(1)) if length_match else 0
                            height_match = re.search(r'(\d+(\.\d+)?)', element.get("height", "0"))
                            height = float(height_match.group(1)) if height_match else 0
                            area = length * height * 2
                        except (ValueError, AttributeError):
                            pass
                    elif element_type == "columns":
                        # For columns, estimate as perimeter * height
                        try:
                            match = re.search(r'(\d+(\.\d+)?)', element.get("dimensions", "0"))
                            size = float(match.group(1)) if match else 0
                            height_match = re.search(r'(\d+(\.\d+)?)', element.get("height", "0"))
                            height = float(height_match.group(1)) if height_match else 0
                            area = size * 4 * height  # Assuming square column
                        except (ValueError, AttributeError):
                            pass
                    elif element_type == "beams":
                        # For beams, estimate as (width + 2*depth) * length
                        try:
                            match = re.search(r'(\d+(\.\d+)?)\s*[xX]\s*(\d+(\.\d+)?)', element.get("dimensions", "0x0"))
                            width = float(match.group(1)) if match else 0
                            depth = float(match.group(3)) if match else 0
                            span_match = re.search(r'(\d+(\.\d+)?)', element.get("span", "0"))
                            length = float(span_match.group(1)) if span_match else 0
                            area = (width + 2 * depth) * length
                        except (ValueError, AttributeError, IndexError):
                            pass
                    elif element_type == "slabs" and element.get("type", "").lower() != "on grade":
                        # For elevated slabs, use area (bottom only)
                        try:
                            area_match = re.search(r'(\d+(\.\d+)?)', element.get("area", "0"))
                            area = float(area_match.group(1)) if area_match else 0
                        except (ValueError, AttributeError):
                            pass
                    
                    # Apply appropriate unit cost
                    if area > 0:
                        form_type = "general"
                        if element_type == "foundations":
                            form_type = "foundation"
                        elif element_type == "walls":
                            form_type = "walls"
                        elif element_type == "columns":
                            form_type = "columns"
                        elif element_type == "beams":
                            form_type = "beams"
                        elif element_type == "slabs" and element.get("type", "").lower() != "on grade":
                            form_type = "elevated_slab"
                        
                        formwork_cost += area * unit_costs["formwork"][form_type]
            
            # If we couldn't calculate detailed formwork, estimate based on concrete volume
            if formwork_cost == 0:
                # Typical formwork is about 40-60 SF per CY of concrete
                formwork_cost = total_volume * 50 * unit_costs["formwork"]["general"]
            
            # Estimate labor cost (typically 35-45% of total cost)
            material_cost = concrete_cost + reinforcement_cost + formwork_cost
            labor_cost = material_cost * 0.4
            
            # Create or update cost estimates
            if "cost_estimates" not in results:
                results["cost_estimates"] = {}
            
            results["cost_estimates"]["estimated_concrete_cost"] = round(concrete_cost, 2) if concrete_cost > 0 else None
            results["cost_estimates"]["estimated_reinforcement_cost"] = round(reinforcement_cost, 2) if reinforcement_cost > 0 else None
            results["cost_estimates"]["estimated_formwork_cost"] = round(formwork_cost, 2) if formwork_cost > 0 else None
            results["cost_estimates"]["estimated_labor_cost"] = round(labor_cost, 2) if labor_cost > 0 else None
            results["cost_estimates"]["currency"] = "USD"
        
        return results