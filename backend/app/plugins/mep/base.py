"""
MEP Base Plugin

This module provides the base class for all MEP (Mechanical, Electrical, Plumbing) plugins.
"""
import json
import logging
from typing import Dict, Any, Optional

import openai
from openai.error import OpenAIError

from app.plugins.base import Plugin

# Set up logging
logger = logging.getLogger(__name__)


class MEPPlugin(Plugin):
    """
    Base class for all MEP (Mechanical, Electrical, Plumbing) plugins.
    """
    
    category = "mep"
    version = "1.0.0"
    
    @property
    def description(self) -> str:
        """
        Default description for MEP plugins.
        """
        return f"Extracts {self.name.lower()} information from construction documents."
    
    async def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyzes the provided text using OpenAI and returns structured data.
        
        Args:
            text: The text to analyze.
            
        Returns:
            A dictionary containing the structured data extracted from the text.
        """
        try:
            # Get the prompt for this specific MEP plugin
            prompt = self._get_analysis_prompt(text)
            
            # Call OpenAI API to analyze the text
            response = await self._call_openai(prompt)
            
            # Parse the response
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse OpenAI response as JSON: {e}")
                return {"error": "Failed to parse response", "details": str(e)}
            
        except Exception as e:
            logger.exception(f"Error in {self.id} analyze method: {e}")
            return {"error": "Analysis failed", "details": str(e)}
    
    def _get_analysis_prompt(self, text: str) -> str:
        """
        Gets the prompt to use for analysis.
        
        Args:
            text: The text to analyze.
            
        Returns:
            The prompt to send to OpenAI.
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    async def _call_openai(self, prompt: str) -> str:
        """
        Calls the OpenAI API with the given prompt.
        
        Args:
            prompt: The prompt to send to OpenAI.
            
        Returns:
            The response from OpenAI.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert in construction and MEP systems. Extract the requested information from the provided text and return it as a valid JSON object."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for more consistent results
                max_tokens=2048
            )
            
            # Extract and return the content
            return response.choices[0].message.content
            
        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise Exception(f"OpenAI API error: {e}")
