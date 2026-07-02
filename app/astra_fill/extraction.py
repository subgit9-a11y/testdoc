import json
import logging
from typing import Dict, Any, Optional
from app.astra_fill.models import HealthIntakeSchema, ConfidenceLevel

logger = logging.getLogger(__name__)

EXTRACTION_SYSTEM_PROMPT = """
You are Astra Fill, a specialized AI utility for extracting structured health information from patient messages.
Your ONLY goal is to extract the following fields into a JSON format.
Do NOT provide medical advice. Do NOT provide a diagnosis. Do NOT add information not present in the text.

Fields to extract:
1. primary_complaint: The main issue or reason for the message.
2. duration: How long the symptom has been present.
3. severity_clues: Any indicators of how bad the pain/issue is (e.g., "cannot sleep", "very sharp").
4. pattern_or_timing: When it happens (e.g., "mornings", "after eating").
5. previous_treatment: Any medicines or remedies mentioned.
6. stop_or_gap_sign: Any mention of stopping a treatment or having a gap in care.
7. is_follow_up: A boolean (true/false) indicating if the patient explicitly mentions this is a follow-up or recurring issue.

If a field is not present, set it to "Not specified" for text fields, or false for boolean fields.

Output EXACTLY this JSON structure and nothing else:
{
  "primary_complaint": "",
  "duration": "",
  "severity_clues": "",
  "pattern_or_timing": "",
  "previous_treatment": "",
  "stop_or_gap_sign": "",
  "is_follow_up": false
}
"""

class HealthExtractor:
    def __init__(self, model_service):
        self.model_service = model_service

    async def extract_health_details(self, text: str, language: str = "en") -> Dict[str, Any]:
        """
        Extracts structured health details from free-text/transcript.
        """
        prompt = f"{EXTRACTION_SYSTEM_PROMPT}\n\nPatient input: \"{text}\"\n\nJSON Output:"
        
        try:
            # Call model service with high temperature for extraction (or low for accuracy?) 
            # Actually low temperature is better for extraction.
            response = await self.model_service.generate_response(
                prompt=prompt,
                language=language,
                max_length=300,
                is_extraction=True
            )
            
            # Find the JSON part in the response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end != -1:
                json_str = response[json_start:json_end]
                extracted_data = json.loads(json_str)
                
                # Basic validation and type safety for Pydantic v2
                schema_fields = HealthIntakeSchema.model_fields
                for field_name, field_info in schema_fields.items():
                    if field_name not in extracted_data:
                        # Set proper defaults based on type
                        if field_info.annotation is bool:
                            extracted_data[field_name] = False
                        elif field_name == "is_follow_up": # Special case if not in annotation
                            extracted_data[field_name] = False
                        else:
                            extracted_data[field_name] = "Not specified"
                    else:
                        # Ensure types are correct
                        if field_info.annotation is bool and not isinstance(extracted_data[field_name], bool):
                            # Try to parse string bools
                            val = str(extracted_data[field_name]).lower()
                            extracted_data[field_name] = val in ('true', 'yes', '1')
                
                # Add confidence scoring logic (Simplified for V1)
                confidences = self._calculate_confidences(extracted_data, text)
                
                return {
                    "structured_data": extracted_data,
                    "confidences": confidences
                }
            else:
                logger.error(f"Failed to find JSON in model response: {response}")
                return self._get_empty_extraction()
                
        except Exception as e:
            logger.error(f"Error during health extraction: {e}")
            return self._get_empty_extraction()

    def _calculate_confidences(self, data: Dict[str, str], original_text: str) -> Dict[str, ConfidenceLevel]:
        """
        Calculates confidence for each field.
        Rule of thumb: If it says 'Not specified', confidence is HIGH (we are sure it's not there).
        If keywords from the extracted value are in the original text, HIGH/MEDIUM.
        """
        confidences = {}
        for field, value in data.items():
            # Handle boolean fields
            if isinstance(value, bool):
                confidences[field] = ConfidenceLevel.HIGH
                continue
                
            if value == "Not specified":
                confidences[field] = ConfidenceLevel.HIGH
            elif isinstance(value, str) and len(value) > 2:
                # Basic check if extraction is actually from the text
                words = value.lower().split()
                matches = sum(1 for word in words if word in original_text.lower())
                if len(words) > 0 and matches / len(words) > 0.5:
                    confidences[field] = ConfidenceLevel.HIGH
                else:
                    confidences[field] = ConfidenceLevel.MEDIUM
            else:
                confidences[field] = ConfidenceLevel.LOW
        return confidences

    def _get_empty_extraction(self) -> Dict[str, Any]:
        empty_data = {
            "primary_complaint": "Not specified",
            "duration": "Not specified",
            "severity_clues": "Not specified",
            "pattern_or_timing": "Not specified",
            "previous_treatment": "Not specified",
            "stop_or_gap_sign": "Not specified"
        }
        return {
            "structured_data": empty_data,
            "confidences": {k: ConfidenceLevel.LOW for k in empty_data.keys()}
        }
    
    # =========================================================================
    # AI-Powered Methods (using api.ayureze.in)
    # =========================================================================
    
    async def ai_extract_health_details(self, text: str, schema_definition: str = None) -> Dict[str, Any]:
        """
        Use AI to extract structured health details from text.
        Uses api.ayureze.in/v1/fill endpoint.
        
        Args:
            text: Patient's message or transcript
            schema_definition: Optional custom schema
        
        Returns:
            Dict with extracted structured data
        """
        try:
            from app.astra_brain_client import get_brain_client
            brain = get_brain_client()
            
            # Use default schema if not provided
            if not schema_definition:
                schema_definition = """
                {
                    "primary_complaint": "string",
                    "duration": "string", 
                    "severity": "string",
                    "timing_pattern": "string",
                    "previous_treatment": "string",
                    "is_follow_up": "boolean"
                }
                """
            
            result = await brain.fill(text, schema_definition)
            
            if result.get("success"):
                logger.info("✅ AI extraction successful")
                try:
                    extracted_data = json.loads(result.get("extracted_data", "{}"))
                except:
                    extracted_data = {"raw": result.get("extracted_data", "")}
                
                return {
                    "structured_data": extracted_data,
                    "confidences": {k: ConfidenceLevel.HIGH for k in extracted_data.keys()},
                    "source": "ai"
                }
            else:
                # Fallback to local extraction
                logger.info("AI extraction failed, using local")
                return await self.extract_health_details(text)
                
        except Exception as e:
            logger.error(f"AI extraction error: {e}")
            return await self.extract_health_details(text)


# Global extractor instance
def get_health_extractor():
    """Get health extractor with model service"""
    from app.model_service import model_service
    return HealthExtractor(model_service)

