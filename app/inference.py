import logging
import json
import os
from typing import Optional
from huggingface_hub import InferenceClient

logger = logging.getLogger(__name__)

class ModelInference:
    """
    Handles model inference operations using HuggingFace Inference API (Serverless).
    """
    
    def __init__(self, base_model_id: str = None, lora_model_id: str = None, device: str = "auto"):
        # Use Qwen 2.5 7B as a powerful non-gated fallback
        self.model_id = "Qwen/Qwen2.5-7B-Instruct" 
        self.token = os.getenv("HF_TOKEN")
        self.client = None
        self.loaded = False
        
        logger.info(f"ModelInference using HF Inference API (Model: {self.model_id})")
        
    async def load_model(self):
        try:
            self.client = InferenceClient(model=self.model_id, token=self.token)
            self.loaded = True
            logger.info(f"✅ Astra AI connected to HF API ({self.model_id})")
        except Exception as e:
            logger.error(f"❌ HF Client Init Failed: {e}")
            self.loaded = False
    
    def is_loaded(self) -> bool:
        return self.loaded and self.client is not None
    
    async def generate_response(self, query: str, language: str = "en", is_extraction: bool = False, **kwargs) -> str:
        if not self.is_loaded(): await self.load_model()
        
        prompt = f"User Query: {query}\n\nLanguage: {language}\n\n"
        if is_extraction: prompt += "Provide only pure JSON data extraction."
        else: prompt += "Provide a helpful response as an Ayurvedic assistant."
        
        try:
            response = self.client.text_generation(
                prompt,
                max_new_tokens=512,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                stop_sequences=["User:", "\n\n"]
            )
            return response.strip()
        except Exception as e:
            logger.error(f"HF Generation Error: {e}")
            return f"Service temporarily busy. ({str(e)})"

    def is_all_ready(self): return True
    def cleanup(self): pass
