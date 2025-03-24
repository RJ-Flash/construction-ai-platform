import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import PyPDF2
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import openai
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from sqlalchemy.orm import Session

from ..core.config import settings
from ..db.models import Document, Element, DocumentSpecification

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

class DocumentAnalysisService:
    """Service for analyzing construction documents and extracting elements."""
    
    def __init__(self, db: Session):
        self.db = db
        self.model_name = os.getenv("DOCUMENT_ANALYSIS_MODEL", "gpt-4")
    
    async def analyze_document(self, document_id: int) -> Dict[str, Any]:
        """
        Analyze a document to extract construction elements and specifications.
        
        Args:
            document_id: ID of the document to analyze
            
        Returns:
            Dict with analysis results
        """
        # Get document from database
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document with ID {document_id} not found")
        
        # Update document status
        document.analysis_status = "processing"
        self.db.commit()
        
        try:
            # Extract text from document
            file_path = document.file_path
            file_text = self._extract_text_from_file(file_path)
            
            # Analyze text with AI
            analysis_results = self._analyze_text_with_ai(file_text)
            
            # Process and save results
            elements = self._process_elements(analysis_results.get("elements", []), document)
            specifications = self._process_specifications(analysis_results.get("specifications", {}), document)
            
            # Update document status
            document.is_analyzed = True
            document.analysis_status = "completed"
            document.analysis_date = datetime.utcnow()
            self.db.commit()
            
            return {
                "document_id": document.id,
                "is_analyzed": True,
                "analysis_status": "completed",
                "elements": elements,
                "specifications": specifications,
                "recommendations": analysis_results.get("recommendations", [])
            }
            
        except Exception as e:
            # Update document status on error
            document.analysis_status = "failed"
            self.db.commit()
            raise e
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """
        Extract text from a file based on its type.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Extracted text
        """
        _, file_extension = os.path.splitext(file_path)
        
        if file_extension.lower() == '.pdf':
            return self._extract_text_from_pdf(file_path)
        elif file_extension.lower() in ['.jpg', '.jpeg', '.png', '.tiff']:
            return self._extract_text_from_image(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def _extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text
        """
        text = ""
        
        # Try to extract text directly first
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page_num in range(len(reader.pages)):
                    page = reader.pages[page_num]
                    page_text = page.extract_text()
                    if page_text.strip():
                        text += page_text + "\n\n"
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
        
        # If text extraction failed or returned little text, try OCR
        if len(text.split()) < 50:
            text = self._extract_text_from_pdf_via_ocr(pdf_path)
        
        return text
    
    def _extract_text_from_pdf_via_ocr(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file using OCR.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text
        """
        text = ""
        
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            
            # Use OCR to extract text from each page
            for i, image in enumerate(images):
                page_text = pytesseract.image_to_string(image, lang='eng')
                text += page_text + "\n\n"
                
        except Exception as e:
            print(f"Error extracting text from PDF via OCR: {e}")
        
        return text
    
    def _extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image file using OCR.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text
        """
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang='eng')
            return text
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""
    
    def _analyze_text_with_ai(self, text: str) -> Dict[str, Any]:
        """
        Analyze text with AI to extract construction elements and specifications.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dict with analysis results
        """
        # Prepare prompt for OpenAI
        system_prompt = """
        You are an expert construction document analyzer. Your task is to analyze the provided 
        construction document text and extract key information:
        
        1. Identify all construction elements (like walls, floors, foundations, etc.)
        2. Extract their properties (materials, dimensions, quantities)
        3. Identify technical specifications
        4. Provide recommendations based on the document content
        
        Format your response as a JSON object with the following structure:
        {
            "elements": [
                {
                    "type": "element type (e.g., Wall, Window, Door)",
                    "materials": "material description",
                    "dimensions": "dimension details",
                    "quantity": numeric value if specified,
                    "estimated_price": null,
                    "notes": "any additional information"
                }
            ],
            "specifications": {
                "category1": [
                    "specification 1",
                    "specification 2"
                ],
                "category2": [
                    "specification 3"
                ]
            },
            "recommendations": [
                "recommendation 1",
                "recommendation 2"
            ]
        }
        
        Only include information that is explicitly stated in the document. 
        If information is not available, use null values.
        """
        
        # Call OpenAI API
        try:
            # For large documents, we might need to break it into chunks
            # For simplicity, we're assuming the document is small enough
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
                    
                # If still can't parse, return empty results
                return {
                    "elements": [],
                    "specifications": {},
                    "recommendations": []
                }
                
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            raise
    
    def _process_elements(self, elements_data: List[Dict[str, Any]], document: Document) -> List[Dict[str, Any]]:
        """
        Process and save extracted elements to the database.
        
        Args:
            elements_data: List of elements extracted from AI
            document: Document these elements belong to
            
        Returns:
            List of processed elements
        """
        saved_elements = []
        
        for element_data in elements_data:
            # Create Element object
            element = Element(
                type=element_data.get("type"),
                materials=element_data.get("materials"),
                dimensions=element_data.get("dimensions"),
                quantity=element_data.get("quantity"),
                estimated_price=element_data.get("estimated_price"),
                notes=element_data.get("notes"),
                document_id=document.id,
                project_id=document.project_id
            )
            
            # Save to database
            self.db.add(element)
            self.db.flush()  # Get ID without committing transaction
            
            # Add to results
            saved_elements.append({
                "id": element.id,
                "type": element.type,
                "materials": element.materials,
                "dimensions": element.dimensions,
                "quantity": element.quantity,
                "estimated_price": element.estimated_price,
                "notes": element.notes
            })
        
        self.db.commit()
        return saved_elements
    
    def _process_specifications(self, specs_data: Dict[str, List[str]], document: Document) -> Dict[str, List[str]]:
        """
        Process and save extracted specifications to the database.
        
        Args:
            specs_data: Specifications extracted from AI
            document: Document these specifications belong to
            
        Returns:
            Dict of processed specifications
        """
        for category, specs in specs_data.items():
            for i, spec_value in enumerate(specs):
                # Create specification object
                spec = DocumentSpecification(
                    category=category,
                    key=f"{category}_{i+1}",
                    value=spec_value,
                    document_id=document.id
                )
                
                # Save to database
                self.db.add(spec)
        
        self.db.commit()
        return specs_data