"""
Unified Storage Client Factory (Wasabi Exclusive)
Handles secure storage of patient documents on Wasabi S3.
"""

import os
import logging
from typing import Optional, List, Dict, Any
from app.wasabi_client import WasabiClient

logger = logging.getLogger(__name__)

class StorageClient:
    """
    Interface for Wasabi document storage.
    """
    
    def __init__(self):
        """Initialize Wasabi storage client"""
        # We now use Wasabi exclusively
        self.provider = "wasabi"
        
        try:
            self.wasabi = WasabiClient()
            if not self.wasabi.is_configured():
                logger.error("❌ WASABI STORAGE IS NOT CONFIGURED. Document features will fail.")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Wasabi client: {e}")
            self.wasabi = None
            
        logger.info("💾 Storage system initialized with WASABI (Exclusive Mode)")
    
    @property
    def bucket_name(self) -> str:
        """Expose the bucket name for audit/logging"""
        if self.wasabi:
            return self.wasabi.bucket_name
        return "unknown"

    def upload_document(
        self, 
        file_path: str, 
        patient_id: str, 
        doc_type: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """Upload to Wasabi"""
        if not self.wasabi or not self.wasabi.is_configured():
            logger.error("Wasabi client not available for upload")
            return None
        return self.wasabi.upload_document(file_path, patient_id, doc_type, metadata)

    def download_document(self, object_key: str, download_path: str) -> bool:
        """Download from Wasabi"""
        if not self.wasabi or not self.wasabi.is_configured():
            return False
        return self.wasabi.download_document(object_key, download_path)

    def generate_download_url(self, object_key: str, expiration_hours: int = 24) -> Optional[str]:
        """Generate Wasabi pre-signed URL"""
        if not self.wasabi or not self.wasabi.is_configured():
            return None
        return self.wasabi.generate_download_url(object_key, expiration_hours)

    def list_patient_documents(self, patient_id: str) -> List[Dict[str, Any]]:
        """List documents from Wasabi EHR"""
        if not self.wasabi or not self.wasabi.is_configured():
            return []
        return self.wasabi.list_patient_documents(patient_id)

    def delete_document(self, object_key: str) -> bool:
        """Delete from Wasabi"""
        if not self.wasabi or not self.wasabi.is_configured():
            return False
        return self.wasabi.delete_document(object_key)

    def get_document_metadata(self, object_key: str) -> Optional[Dict[str, Any]]:
        """Get document metadata from Wasabi"""
        if not self.wasabi or not self.wasabi.is_configured():
            return None
        return self.wasabi.get_document_metadata(object_key)

# Singleton instance
storage_client = StorageClient()

def get_storage_client() -> StorageClient:
    """Get the global storage client instance"""
    return storage_client
