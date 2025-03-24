"""
AI Service for Construction Document Analysis.
Provides functionality for document parsing, element detection, and cost estimation.
"""
import os
from typing import Dict, List, Optional, Tuple
import logging
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load environment variables
load_dotenv()
logger = logging.getLogger(__name__)

class AIService:
    """AI Service for analyzing construction documents and generating quotes."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI service with OpenAI API key."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize the LLM
        self.llm = ChatOpenAI(
            openai_api_key=self.api_key,
            model_name="gpt-4o",
            temperature=0.2
        )
    
    def analyze_document(self, document_path: str) -> Dict:
        """
        Analyze a construction document to extract key elements and specifications.
        
        Args:
            document_path: Path to the PDF document
            
        Returns:
            Dictionary containing extracted elements and specifications
        """
        try:
            # Load and parse the document
            loader = PyPDFLoader(document_path)
            documents = loader.load()
            
            # Split the document for processing
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,
                chunk_overlap=200
            )
            chunks = text_splitter.split_documents(documents)
            
            # Process each chunk to extract construction elements
            results = self._process_document_chunks(chunks)
            
            return {
                "success": True,
                "elements": results["elements"],
                "specifications": results["specifications"],
                "recommendations": results["recommendations"]
            }
            
        except Exception as e:
            logger.error(f"Error analyzing document: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _process_document_chunks(self, chunks: List) -> Dict:
        """Process document chunks to extract construction information."""
        # Template for extracting construction elements
        element_extraction_template = PromptTemplate(
            input_variables=["chunk_text"],
            template="""
            Analyze the following construction document excerpt and extract all relevant construction elements.
            For each element, identify:
            1. Type (e.g., wall, foundation, roof, window, door, etc.)
            2. Dimensions (if available)
            3. Materials specified
            4. Quantity (if available)
            5. Any special requirements or notes
            
            Document excerpt:
            {chunk_text}
            
            Provide the results in a structured format.
            """
        )
        
        element_chain = LLMChain(llm=self.llm, prompt=element_extraction_template)
        
        # Process each chunk
        all_elements = []
        specifications = {}
        recommendations = []
        
        for i, chunk in enumerate(chunks):
            if i > 10:  # Limit processing for very large documents
                break
                
            result = element_chain.run(chunk_text=chunk.page_content)
            # Parse the results and aggregate
            # Note: In a production system, we would implement a more robust parser
            parsed_elements = self._parse_element_results(result)
            all_elements.extend(parsed_elements)
            
        # Deduplicate elements
        unique_elements = self._deduplicate_elements(all_elements)
        
        # Generate specifications and recommendations
        specifications = self._extract_specifications(chunks)
        recommendations = self._generate_recommendations(unique_elements, specifications)
        
        return {
            "elements": unique_elements,
            "specifications": specifications,
            "recommendations": recommendations
        }
    
    def _parse_element_results(self, result: str) -> List[Dict]:
        """Parse the LLM output to extract structured elements."""
        # This is a simplified parser that would be more robust in production
        elements = []
        # Simple parsing logic for demonstration purposes
        lines = result.strip().split("\n")
        current_element = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("Type:") or (not current_element and ":" in line):
                # If we were working on a previous element, add it to our list
                if current_element:
                    elements.append(current_element)
                    
                # Start a new element
                current_element = {}
            
            if ":" in line:
                key, value = line.split(":", 1)
                current_element[key.strip().lower()] = value.strip()
        
        # Add the last element if it exists
        if current_element:
            elements.append(current_element)
            
        return elements
    
    def _deduplicate_elements(self, elements: List[Dict]) -> List[Dict]:
        """Remove duplicate elements based on type and dimensions."""
        # Simple deduplication for demonstration
        unique_elements = []
        seen_signatures = set()
        
        for element in elements:
            # Create a signature for this element
            if "type" in element and "dimensions" in element:
                signature = f"{element['type']}_{element['dimensions']}"
            elif "type" in element:
                signature = element["type"]
            else:
                # If we can't create a signature, just add it
                unique_elements.append(element)
                continue
                
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                unique_elements.append(element)
                
        return unique_elements
    
    def _extract_specifications(self, chunks: List) -> Dict:
        """Extract project specifications from the document."""
        # Template for extracting specifications
        spec_template = PromptTemplate(
            input_variables=["chunk_text"],
            template="""
            Extract the key project specifications from the following construction document:
            
            {chunk_text}
            
            Include information about:
            1. Building codes and standards referenced
            2. Quality requirements
            3. Material specifications
            4. Testing requirements
            5. Other important specifications
            
            Provide results in a structured format.
            """
        )
        
        spec_chain = LLMChain(llm=self.llm, prompt=spec_template)
        
        # Combine some chunks for better context
        combined_text = "\n".join([chunk.page_content for chunk in chunks[:3]])
        result = spec_chain.run(chunk_text=combined_text)
        
        # Simple parsing for demonstration
        specifications = {}
        current_section = "general"
        
        for line in result.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
                
            if line.endswith(":") and len(line) < 50:  # Likely a section header
                current_section = line[:-1].lower()
                specifications[current_section] = []
            else:
                if current_section not in specifications:
                    specifications[current_section] = []
                specifications[current_section].append(line)
                
        return specifications
    
    def _generate_recommendations(self, elements: List[Dict], specifications: Dict) -> List[str]:
        """Generate recommendations based on the analyzed elements and specifications."""
        # Simplified recommendation generation
        recommendations = []
        
        # Count element types
        element_counts = {}
        for element in elements:
            if "type" in element:
                element_type = element["type"]
                element_counts[element_type] = element_counts.get(element_type, 0) + 1
        
        # Generate basic recommendations
        if "wall" in element_counts and element_counts["wall"] > 5:
            recommendations.append("Consider bulk purchasing of wall materials to reduce costs")
            
        if "window" in element_counts and element_counts["window"] > 10:
            recommendations.append("High window count - verify energy efficiency ratings")
            
        if "foundation" in element_counts:
            recommendations.append("Ensure foundation specifications meet local soil conditions")
            
        # Add general recommendations
        recommendations.append("Verify all materials meet or exceed specified quality standards")
        recommendations.append("Consider weather conditions for project scheduling")
        
        return recommendations
    
    def generate_quote(self, elements: List[Dict], region: str) -> Dict:
        """
        Generate a cost estimate based on extracted elements.
        
        Args:
            elements: List of construction elements
            region: Geographic region for pricing adjustments
            
        Returns:
            Dictionary with cost estimates
        """
        # Template for cost estimation
        quote_template = PromptTemplate(
            input_variables=["elements", "region"],
            template="""
            Generate a detailed cost estimate for the following construction elements in the {region} region:
            
            {elements}
            
            For each element category, provide:
            1. Material costs (estimated range)
            2. Labor costs (estimated range)
            3. Equipment costs if applicable
            4. Time estimates for installation/construction
            
            Also provide:
            - Subtotal for each category
            - Overall project total estimate (range)
            - Notes about potential cost variations
            """
        )
        
        quote_chain = LLMChain(llm=self.llm, prompt=quote_template)
        
        try:
            # Format elements for the prompt
            elements_text = "\n".join([f"- {element.get('type', 'Unknown')}: " + 
                                      f"{element.get('dimensions', 'N/A')} - " +
                                      f"{element.get('materials', 'N/A')}" +
                                      f" (Quantity: {element.get('quantity', '1')})"
                                      for element in elements])
            
            result = quote_chain.run(elements=elements_text, region=region)
            
            # In a production system, we would parse this into a more structured format
            # For now, we'll return a simplified version
            return {
                "success": True,
                "quote_details": result,
                "raw_quote": result  # In production, we would parse this into sections
            }
            
        except Exception as e:
            logger.error(f"Error generating quote: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
