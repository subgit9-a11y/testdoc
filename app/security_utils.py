import re
import logging

logger = logging.getLogger("AstraSecurityUtils")

# PII Masking Patterns
PHONE_PATTERN = re.compile(r'(\+91[\s\-]?)?(\d{5})[\s\-]?(\d{5})')
EMAIL_PATTERN = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')

def mask_pii(text: str) -> str:
    """
    Masks Phone and Email in logs for DISHA compliance.
    Example: +91-89689 68156 -> +91-89689 *****
    """
    if not text or not isinstance(text, str):
        return text
    
    # Masking Email
    text = EMAIL_PATTERN.sub("****@****.***", text)
    
    # Masking Phone
    def obscure_phone(match):
        prefix = match.group(1) or ""
        first_half = match.group(2)
        return f"{prefix}{first_half}*****"
    
    text = PHONE_PATTERN.sub(obscure_phone, text)
    return text

def detect_prompt_injection(text: str) -> bool:
    """
    Heuristic detection of 'Prompt Injection' attacks.
    Checks for keywords that try to override AI instructions.
    """
    if not text:
        return False
        
    danger_keywords = [
        "ignore previous instructions",
        "system prompt",
        "DAN mode",
        "forget everything",
        "jailbreak",
        "act as a", # Common injection start
        "respond as",
        "bypass",
        "administrator mode"
    ]
    
    text_lower = text.lower()
    for kw in danger_keywords:
        if kw in text_lower:
            logger.warning(f"🚨 INJECTION ATTEMPT DETECTED: Found keyword '{kw}'")
            return True
            
    # Check for long repetition injection
    if len(text) > 4000:
        logger.warning(f"🚨 POTENTIAL DoS: Large payload detected ({len(text)} chars)")
        return True
        
    return False
