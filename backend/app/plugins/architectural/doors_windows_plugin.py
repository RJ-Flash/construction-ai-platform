from typing import Dict, Any, List
import json
import re
import openai
import os
from ...plugins.base import AnalysisPlugin
from ...plugins.registry import register_plugin

@register_plugin
class DoorsWindowsPlugin(AnalysisPlugin):
    """Plugin for analyzing doors and windows in construction documents."""
    
    id = "architectural.doors_windows"
    name = "Doors and Windows Quantifier"
    version = "1.0.0"
    description = "Analyzes construction documents to extract doors and windows details, including types, sizes, quantities, and specifications."
    author = "Construction AI Platform"
    category = "architectural"
    price = 149.0
    
    def __init__(self):
        super().__init__()
        self.model_name = os.getenv("DOCUMENT_ANALYSIS_MODEL", "gpt-4")
    
    async def analyze(self, text: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze construction documents for doors and windows.
        
        Args:
            text: Document text content
            context: Additional context information
            
        Returns:
            Dictionary with extracted door and window information
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
            You are an expert in analyzing construction documents for doors and windows. 
            Your task is to extract detailed information about doors and windows from the provided text.
            
            Specifically, identify:
            1. Door types (e.g., solid core, hollow core, fire-rated, sliding, bi-fold)
            2. Door materials (e.g., wood, metal, glass, fiberglass)
            3. Door dimensions (width, height, thickness)
            4. Door hardware and accessories
            5. Window types (e.g., fixed, casement, double-hung, sliding, awning)
            6. Window materials (e.g., vinyl, aluminum, wood, fiberglass)
            7. Window dimensions
            8. Window glazing specifications (e.g., insulated, tempered, low-E)
            9. Energy efficiency ratings
            10. Special requirements or details
            
            Format your response as a JSON object with the following structure:
            {
                "doors": [
                    {
                        "type": "door type",
                        "subtype": "door subtype (if applicable)",
                        "material": "primary material",
                        "width": "door width",
                        "height": "door height",
                        "thickness": "door thickness",
                        "hardware": "hardware details",
                        "fire_rating": "fire rating (if specified)",
                        "location": "location description if available",
                        "frame_type": "frame type if specified",
                        "finish": "door finish",
                        "special_requirements": "any special details",
                        "quantity": quantity value or null,
                        "tag": "door tag or identifier (if available)"
                    }
                ],
                "windows": [
                    {
                        "type": "window type",
                        "material": "primary material",
                        "width": "window width",
                        "height": "window height",
                        "glazing": "glazing specifications",
                        "energy_rating": "energy efficiency rating if specified",
                        "operation": "how the window operates",
                        "frame_type": "frame type",
                        "location": "location description if available",
                        "special_requirements": "any special details",
                        "quantity": quantity value or null,
                        "tag": "window tag or identifier (if available)"
                    }
                ],
                "door_schedule": [
                    {
                        "tag": "door tag/identifier",
                        "count": count value or null,
                        "remarks": "any schedule remarks"
                    }
                ],
                "window_schedule": [
                    {
                        "tag": "window tag/identifier",
                        "count": count value or null,
                        "remarks": "any schedule remarks"
                    }
                ],
                "cost_estimates": {
                    "doors_total_count": total number of doors or null,
                    "windows_total_count": total number of windows or null,
                    "estimated_doors_cost": estimated doors cost value or null,
                    "estimated_windows_cost": estimated windows cost value or null,
                    "currency": "USD"
                },
                "notes": [
                    "any general notes about the doors and windows"
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
        if "cost_estimates" not in results or not results["cost_estimates"].get("estimated_doors_cost"):
            # Default costs for different door and window types
            door_costs = {
                "hollow core": 150.0,
                "solid core": 250.0,
                "fire rated": 350.0,
                "metal": 400.0,
                "glass": 500.0,
                "sliding": 450.0,
                "bi-fold": 300.0,
                "pocket": 350.0,
                "french": 550.0,
                "general": 300.0  # Default
            }
            
            window_costs = {
                "fixed": 300.0,
                "single hung": 350.0,
                "double hung": 400.0,
                "casement": 450.0,
                "awning": 400.0,
                "sliding": 450.0,
                "bay": 1200.0,
                "bow": 1500.0,
                "picture": 600.0,
                "general": 400.0  # Default
            }
            
            # Calculate door costs
            door_count = 0
            door_cost = 0
            for door in results.get("doors", []):
                quantity = door.get("quantity", 1)
                door_count += quantity
                
                # Try to determine door type and use appropriate cost
                door_type = door.get("type", "").lower()
                unit_cost = door_costs.get("general")  # Default
                for door_type_key, cost in door_costs.items():
                    if door_type_key in door_type:
                        unit_cost = cost
                        break
                
                # Adjust cost based on size if available
                width = 0
                try:
                    width_match = re.search(r'(\d+(\.\d+)?)', door.get("width", "0"))
                    if width_match:
                        width = float(width_match.group(1))
                except (ValueError, AttributeError):
                    pass
                
                # Standard door is about 36" wide
                if width > 42:
                    unit_cost *= 1.25  # 25% premium for oversized doors
                
                door_cost += quantity * unit_cost
            
            # Calculate window costs
            window_count = 0
            window_cost = 0
            for window in results.get("windows", []):
                quantity = window.get("quantity", 1)
                window_count += quantity
                
                # Try to determine window type and use appropriate cost
                window_type = window.get("type", "").lower()
                unit_cost = window_costs.get("general")  # Default
                for window_type_key, cost in window_costs.items():
                    if window_type_key in window_type:
                        unit_cost = cost
                        break
                
                # Adjust cost based on size if available
                area = 0
                try:
                    width_match = re.search(r'(\d+(\.\d+)?)', window.get("width", "0"))
                    height_match = re.search(r'(\d+(\.\d+)?)', window.get("height", "0"))
                    if width_match and height_match:
                        width = float(width_match.group(1))
                        height = float(height_match.group(1))
                        area = width * height
                except (ValueError, AttributeError):
                    pass
                
                # Standard window area is about 15 square feet
                if area > 20:
                    unit_cost *= (area / 15)  # Proportional increase for larger windows
                
                # Adjust cost for special glazing
                glazing = window.get("glazing", "").lower()
                if "low-e" in glazing or "low e" in glazing:
                    unit_cost *= 1.1  # 10% premium for low-E glazing
                if "tempered" in glazing:
                    unit_cost *= 1.15  # 15% premium for tempered glass
                if "insulated" in glazing or "double" in glazing:
                    unit_cost *= 1.2  # 20% premium for insulated glass
                if "triple" in glazing:
                    unit_cost *= 1.3  # 30% premium for triple glazing
                
                window_cost += quantity * unit_cost
            
            # Create or update cost estimates
            if "cost_estimates" not in results:
                results["cost_estimates"] = {}
            
            # Use door counts from schedule if available
            if not door_count and results.get("door_schedule"):
                door_count = sum(schedule.get("count", 0) for schedule in results.get("door_schedule", []))
            
            # Use window counts from schedule if available
            if not window_count and results.get("window_schedule"):
                window_count = sum(schedule.get("count", 0) for schedule in results.get("window_schedule", []))
            
            results["cost_estimates"]["doors_total_count"] = door_count if door_count > 0 else None
            results["cost_estimates"]["windows_total_count"] = window_count if window_count > 0 else None
            results["cost_estimates"]["estimated_doors_cost"] = round(door_cost, 2) if door_cost > 0 else None
            results["cost_estimates"]["estimated_windows_cost"] = round(window_cost, 2) if window_cost > 0 else None
            results["cost_estimates"]["currency"] = "USD"
        
        return results