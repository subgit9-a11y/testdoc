import logging
from .custom_whatsapp_client import CustomWhatsAppClient

logger = logging.getLogger(__name__)

# This is a compatibility layer to ensure that any code expecting 
# MetaWhatsAppClient still works with the new CustomWhatsAppClient.

class MetaWhatsAppClient(CustomWhatsAppClient):
    """Compatibility wrapper for CustomWhatsAppClient"""
    def __init__(self, *args, **kwargs):
        try:
            super().__init__(*args, **kwargs)
        except Exception as e:
            logger.warning(f"MetaWhatsAppClient (wrapped) initialization failed: {e}")
            # Do not raise here to prevent startup crashes
            pass

    # Ensure all methods are accessible with the same names if needed
    # (they already should be via inheritance)
