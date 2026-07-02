"""
Astra Dosage Intelligence System
Uses AI to calculate correct medicine doses based on patient profile and symptoms.
Integrates with the Astra Brain for clinical-grade precision.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from app.astra_brain_client import get_brain_client

logger = logging.getLogger(__name__)

class DosageIntelligence:
    """Calculates and suggests safe dosages for medications"""
    
    def __init__(self):
        self.brain = None
        logger.info("Astra Dosage Intelligence Initialized")

    @property
    def brain_client(self):
        """Lazy load brain client"""
        if self.brain is None:
            self.brain = get_brain_client()
        return self.brain

    async def suggest_dosage(self, medicine_name: str, patient_profile: Dict[str, Any], symptoms: List[str]) -> Dict[str, Any]:
        """
        Suggests clinical dosage for a medicine.
        
        Args:
            medicine_name: Name of the medicine (e.g., 'Ashwagandha')
            patient_profile: dict with 'age', 'gender', 'weight_kg' (optional)
            symptoms: list of symptoms
        
        Returns: 
            Dict: { 'dose': '500mg', 'frequency': 'twice_daily', 'timing': 'After Food', 'duration': '15 days', 'reasoning': ... }
        """
        try:
            # Construct a precision prompt for the brain's /v1/fill endpoint
            # asking it to return a JSON dosage schema.
            schema = {
                "dose": "string (e.g., 5-10ml, 500mg, 1 tablet)",
                "frequency": "string (once_daily, twice_daily, thrice_daily)",
                "timing": "string (Before Food, After Food, Empty Stomach)",
                "duration": "string (7 days, 1 month)",
                "reasoning": "string (Clinical logic based on age/symptoms)"
            }
            
            prompt = (
                f"PATIENT: {patient_profile['age']} year old {patient_profile['gender']}.\n"
                f"SYMPTOMS: {', '.join(symptoms)}\n"
                f"MEDICINE: {medicine_name}\n"
                "Calculate the standard Ayurvedic dosage for this patient. Always exercise clinical safety."
            )
            
            result = await self.brain_client.fill(prompt, json.dumps(schema))
            
            if result.get("success"):
                try:
                    # The fill endpoint returns 'result' as the filled JSON
                    res_val = result.get("result", "{}")
                    dosage = json.loads(res_val) if isinstance(res_val, str) else res_val
                    return {
                        "success": True, 
                        "dosage": dosage,
                        "source": "astra_dosage_engine_ai"
                    }
                except: pass
            
            # Fallback for generic dosage
            return {
                "success": False,
                "dosage": {
                    "dose": "As directed", 
                    "frequency": "twice_daily", 
                    "timing": "After Food", 
                    "duration": "30 days",
                    "reasoning": "Generic fallback due to AI connectivity issue"
                }
            }
            
        except Exception as e:
            logger.error(f"Dosage calculation error: {e}")
            return {"success": False, "error": str(e)}

# Global Dosage singleton
dosage_service = DosageIntelligence()
