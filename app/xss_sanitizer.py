"""
AI Output Sanitizer (XSS Prevention)
Protects the platform from AI-Driven Cross-Site Scripting attacks.
"""

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class XSSSanitizer:
    """
    Strips dangerous HTML/JavaScript payloads from user inputs and AI outputs.
    Ensures that if the AI is tricked into repeating malicious code, it cannot 
    execute in the Admin Web Panel or Flutter App.
    """
    
    def __init__(self):
        # Extremely aggressive regex to match any HTML tags or script blocks
        self.html_tag_pattern = re.compile(r'<[^>]*?>')
        self.script_event_pattern = re.compile(r'(javascript:|onload=|onerror=|eval\()', re.IGNORECASE)

    def sanitize_text(self, text: str) -> str:
        """
        Removes HTML tags and neutralizes dangerous JavaScript keywords.
        """
        if not text or not isinstance(text, str):
            return text
            
        # 1. Strip all HTML tags completely (e.g., <script>, <img>, <iframe>)
        clean_text = re.sub(self.html_tag_pattern, '', text)
        
        # 2. Neutralize inline javascript events (e.g., javascript:alert(1))
        # We replace the colon or equal sign to break the executable signature
        clean_text = re.sub(self.script_event_pattern, '[REDACTED]', clean_text)
        
        # Log if malicious content was found and stripped
        if len(clean_text) != len(text):
            logger.warning("🛡️ XSS Sanitizer intercepted and neutralized potential malicious HTML/Script payload.")
            
        return clean_text.strip()

    def sanitize_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively sanitizes a JSON dictionary payload.
        """
        sanitized = {}
        for k, v in payload.items():
            if isinstance(v, str):
                sanitized[k] = self.sanitize_text(v)
            elif isinstance(v, dict):
                sanitized[k] = self.sanitize_payload(v)
            elif isinstance(v, list):
                sanitized[k] = [self.sanitize_text(i) if isinstance(i, str) else i for i in v]
            else:
                sanitized[k] = v
        return sanitized

# Global instance
xss_sanitizer = XSSSanitizer()
