import os
import math
import logging
from typing import Dict, List, Any, Tuple
import re
import cv2
import numpy as np
import PyPDF2
import pytesseract
from PIL import Image

from app.db.models.element import ElementType

# Set up logger
logger = logging.getLogger(__name__)

def process_pdf(file_path: str) -> Dict[str, Any]:
    """
    Process a PDF file to extract elements, dimensions, and other information.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        dict: Processing results including extracted elements, scale, confidence, etc.
    """
    try:
        # Open the PDF file
        pdf_file = PyPDF2.PdfReader(file_path)
        page_count = len(pdf_file.pages)
        
        # Initialize results
        result = {
            'elements': [],
            'text': '',
            'scale_factor': 1.0,
            'confidence_score': 0.0,
        }
        
        total_confidence = 0.0
        
        # Process each page
        for page_num in range(page_count):
            # Extract text from the page
            page = pdf_file.pages[page_num]
            page_text = page.extract_text() or ""
            result['text'] += page_text + "\n\n"
            
            # Convert PDF page to image for CV processing
            # This would normally use a proper PDF to image conversion
            # For simplicity, we're mocking the extraction process
            
            # In a real implementation, we would:
            # 1. Convert PDF page to image
            # 2. Preprocess the image (denoise, enhance, etc.)
            # 3. Detect lines, shapes, and text using OpenCV
            # 4. Identify elements and their dimensions
            
            # Mock detection of walls
            walls = _detect_walls_from_text(page_text)
            result['elements'].extend(walls)
            
            # Mock detection of doors and windows
            openings = _detect_openings_from_text(page_text)
            result['elements'].extend(openings)
            
            # Mock detection of annotations
            annotations = _detect_annotations(page_text)
            result['elements'].extend(annotations)
            
            # Extract scale information
            scale = _extract_scale(page_text)
            if scale > 0:
                result['scale_factor'] = scale
                
            # Calculate confidence for this page
            detected_element_count = len(walls) + len(openings) + len(annotations)
            if detected_element_count > 0:
                # Higher confidence if more elements detected
                page_confidence = min(0.95, 0.5 + (detected_element_count / 100))
            else:
                page_confidence = 0.3
                
            total_confidence += page_confidence
        
        # Average confidence across all pages
        if page_count > 0:
            result['confidence_score'] = total_confidence / page_count
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing PDF file {file_path}: {str(e)}")
        raise
        

def _detect_walls_from_text(text: str) -> List[Dict[str, Any]]:
    """Extract wall information from text using regex patterns."""
    walls = []
    
    # Look for patterns like "Wall: 10' x 8'" or "Wall W1: L=20', H=10'"
    wall_patterns = [
        r"Wall[:\s]*(\w+)?[:\s]*(?:L=)?(\d+\.?\d*)[\'\"]?(?:\s*x\s*|\s*[,xX]\s*H=)(\d+\.?\d*)[\'\"]?",
        r"(\d+\.?\d*)[\'\"]?\s*(?:x|X)\s*(\d+\.?\d*)[\'\"]?\s*wall",
    ]
    
    for pattern in wall_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            # Extract dimensions based on which pattern matched
            if len(match.groups()) == 3:
                wall_name = match.group(1) or f"Wall-{len(walls)+1}"
                length = float(match.group(2))
                height = float(match.group(3))
            else:
                wall_name = f"Wall-{len(walls)+1}"
                length = float(match.group(1))
                height = float(match.group(2))
            
            walls.append({
                'element_type': ElementType.WALL,
                'name': wall_name,
                'description': f"Wall {wall_name} - {length}' x {height}'",
                'length': length,
                'height': height,
                'width': 0.5,  # Assuming standard wall width
                'area': length * height,
                'volume': length * height * 0.5,
                'confidence_score': 0.85,
                'detection_method': 'text_regex',
                'coordinates': {"type": "rectangle", "x1": 0, "y1": 0, "x2": 0, "y2": 0}  # Placeholder
            })
    
    return walls


def _detect_openings_from_text(text: str) -> List[Dict[str, Any]]:
    """Extract door and window information from text."""
    openings = []
    
    # Door patterns: "Door: 3' x 7'" or "Door D1: W=3', H=7'"
    door_patterns = [
        r"Door[:\s]*(\w+)?[:\s]*(?:W=)?(\d+\.?\d*)[\'\"]?(?:\s*x\s*|\s*[,xX]\s*H=)(\d+\.?\d*)[\'\"]?",
    ]
    
    # Window patterns: "Window: 4' x 3'" or "Window W1: W=4', H=3'"
    window_patterns = [
        r"Window[:\s]*(\w+)?[:\s]*(?:W=)?(\d+\.?\d*)[\'\"]?(?:\s*x\s*|\s*[,xX]\s*H=)(\d+\.?\d*)[\'\"]?",
    ]
    
    # Process doors
    for pattern in door_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            door_name = match.group(1) or f"Door-{len(openings)+1}"
            width = float(match.group(2))
            height = float(match.group(3))
            
            openings.append({
                'element_type': ElementType.DOOR,
                'name': door_name,
                'description': f"Door {door_name} - {width}' x {height}'",
                'width': width,
                'height': height,
                'area': width * height,
                'confidence_score': 0.8,
                'detection_method': 'text_regex',
                'coordinates': {"type": "rectangle", "x1": 0, "y1": 0, "x2": 0, "y2": 0}  # Placeholder
            })
    
    # Process windows
    for pattern in window_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            window_name = match.group(1) or f"Window-{len(openings)+1}"
            width = float(match.group(2))
            height = float(match.group(3))
            
            openings.append({
                'element_type': ElementType.WINDOW,
                'name': window_name,
                'description': f"Window {window_name} - {width}' x {height}'",
                'width': width,
                'height': height,
                'area': width * height,
                'confidence_score': 0.8,
                'detection_method': 'text_regex',
                'coordinates': {"type": "rectangle", "x1": 0, "y1": 0, "x2": 0, "y2": 0}  # Placeholder
            })
    
    return openings


def _detect_annotations(text: str) -> List[Dict[str, Any]]:
    """Extract annotations like notes, dimensions, specifications."""
    annotations = []
    
    # Look for note patterns: "Note: ..." or "General Notes: ..."
    note_patterns = [
        r"(?:General\s*)?Note[s]?[:\s]*(.*?)(?:\n\n|\Z)",
        r"(?:General\s*)?Specification[s]?[:\s]*(.*?)(?:\n\n|\Z)",
    ]
    
    for pattern in note_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            note_text = match.group(1).strip()
            if len(note_text) > 10:  # Avoid empty or very short notes
                annotations.append({
                    'element_type': ElementType.ANNOTATION,
                    'name': f"Note-{len(annotations)+1}",
                    'description': note_text[:100] + ("..." if len(note_text) > 100 else ""),
                    'confidence_score': 0.75,
                    'detection_method': 'text_regex',
                    'coordinates': {"type": "point", "x": 0, "y": 0}  # Placeholder
                })
    
    return annotations


def _extract_scale(text: str) -> float:
    """Extract scale information from text."""
    # Look for scale patterns like "Scale: 1/4\" = 1'-0\"" or "Scale: 1:100"
    scale_patterns = [
        r"Scale[:\s]*(\d+)(?:/(\d+))?\"\s*=\s*(\d+)\'(?:-(\d+)\")?",  # Imperial: 1/4" = 1'-0"
        r"Scale[:\s]*(\d+):(\d+)",  # Metric: 1:100
    ]
    
    for pattern in scale_patterns:
        matches = re.search(pattern, text, re.IGNORECASE)
        if matches:
            groups = matches.groups()
            
            # Imperial scale
            if len(groups) >= 3 and groups[2]:
                numerator = int(groups[0])
                denominator = int(groups[1]) if groups[1] else 1
                feet = int(groups[2])
                inches = int(groups[3]) if groups[3] else 0
                
                # Convert to decimal scale factor
                drawing_units = numerator / denominator  # in inches
                real_units = feet * 12 + inches  # in inches
                
                # Scale factor is how many real-world units per drawing unit
                scale_factor = real_units / drawing_units
                return scale_factor
            
            # Metric scale
            elif len(groups) >= 2 and groups[1]:
                # For 1:100, 1 unit on drawing = 100 units in real world
                scale_factor = int(groups[1]) / int(groups[0])
                return scale_factor
    
    # Default scale if not found
    return 1.0
