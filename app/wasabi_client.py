"""
Wasabi S3-Compatible Storage Client for Medical Documents (EHR)
Handles secure upload, download, and sharing of patient documents on Wasabi
Wasabi provides better persistence and accessibility for EHR management.
"""

import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)

class WasabiClient:
    """Client for Wasabi S3 storage with medical document/EHR focus"""
    
    def __init__(self):
        """Initialize Wasabi client with S3-compatible gateway"""
        self.access_key = os.getenv('WASABI_ACCESS_KEY')
        self.secret_key = os.getenv('WASABI_SECRET_KEY')
        self.endpoint = os.getenv('WASABI_ENDPOINT', 'https://s3.wasabisys.com')
        self.bucket_name = os.getenv('WASABI_BUCKET', 'ayureze-medical-records')
        self.region = os.getenv('WASABI_REGION', 'us-east-1')
        
        if not self.access_key or not self.secret_key:
            logger.warning("Wasabi credentials not found in environment variables. Falling back to Storj format check.")
            # If Wasabi is not yet set, we might be in transition. 
            # We don't raise ValueError immediately to allow the factory to handle fallback.
            return
        
        # Initialize S3-compatible client with Wasabi-specific configuration
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            config=Config(
                signature_version='s3v4',
                s3={'addressing_style': 'virtual'} # Wasabi prefers virtual host style
            )
        )
        
        logger.info(f"✅ Wasabi client initialized. Bucket: {self.bucket_name}, Endpoint: {self.endpoint}")
    
    def is_configured(self) -> bool:
        """Check if Wasabi is properly configured"""
        return hasattr(self, 's3_client') and self.s3_client is not None

    def upload_document(
        self, 
        file_path: str, 
        patient_id: str, 
        doc_type: str,
        metadata: Optional[Dict[str, str]] = None
    ) -> Optional[str]:
        """
        Upload medical document to Wasabi
        
        Args:
            file_path: Local path to the document
            patient_id: Patient identifier
            doc_type: Document type (prescription, lab_report, xray, etc.)
            metadata: Additional metadata
        
        Returns:
            Object key if successful, None otherwise
        """
        if not self.is_configured():
            logger.error("Wasabi client not configured")
            return None

        try:
            filename = os.path.basename(file_path)
            
            # Create secure folder structure using hashed patient ID for privacy (consistent with previous Storj logic)
            patient_hash = hashlib.sha256(patient_id.encode()).hexdigest()[:16]
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            object_key = f"patients/{patient_hash}/{doc_type}/{timestamp}_{filename}"
            
            # Prepare metadata (EHR focused)
            doc_metadata = {
                'patient-id': str(patient_id),
                'doc-type': str(doc_type),
                'upload-timestamp': datetime.now(timezone.utc).isoformat(),
                'original-filename': str(filename),
                'storage-provider': 'wasabi'
            }
            
            if metadata:
                # Convert all metadata values to strings for S3 compatibility
                for k, v in metadata.items():
                    doc_metadata[k] = str(v)
            
            # Upload file
            with open(file_path, 'rb') as file_data:
                self.s3_client.put_object(
                    Bucket=self.bucket_name,
                    Key=object_key,
                    Body=file_data,
                    ContentType=self._get_content_type(filename),
                    Metadata=doc_metadata
                )
            
            logger.info(f"✅ Document uploaded to Wasabi: {object_key}")
            return object_key
            
        except Exception as e:
            logger.error(f"❌ Wasabi upload failed for {file_path}: {e}")
            return None
    
    def download_document(self, object_key: str, download_path: str) -> bool:
        """
        Download document from Wasabi
        """
        if not self.is_configured(): return False
        try:
            Path(download_path).parent.mkdir(parents=True, exist_ok=True)
            self.s3_client.download_file(self.bucket_name, object_key, download_path)
            return True
        except Exception as e:
            logger.error(f"Wasabi download failed for {object_key}: {e}")
            return False
    
    def generate_download_url(
        self, 
        object_key: str, 
        expiration_hours: int = 24
    ) -> Optional[str]:
        """
        Generate time-limited pre-signed download URL for patient EHR sharing
        """
        if not self.is_configured(): return None
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': object_key
                },
                ExpiresIn=expiration_hours * 3600
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate Wasabi URL for {object_key}: {e}")
            return None

    def object_exists(self, object_key: str) -> bool:
        """Check if object exists in Wasabi bucket"""
        if not self.is_configured(): return False
        try:
            self.s3_client.head_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except ClientError as e:
            if e.response.get('Error', {}).get('Code') == "404":
                return False
            logger.error(f"Wasabi existence check error: {e}")
            return False
        except Exception as e:
            if "404" in str(e): return False
            logger.error(f"Wasabi existence check error: {e}")
            return False

    def list_patient_documents(self, patient_id: str) -> List[Dict[str, Any]]:
        """
        List all EHR documents for a specific patient in Wasabi
        """
        if not self.is_configured(): return []
        try:
            patient_hash = hashlib.sha256(patient_id.encode()).hexdigest()[:16]
            prefix = f"patients/{patient_hash}/"
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            documents = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    meta_response = self.s3_client.head_object(
                        Bucket=self.bucket_name,
                        Key=obj['Key']
                    )
                    
                    documents.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].isoformat(),
                        'metadata': meta_response.get('Metadata', {}),
                        'content_type': meta_response.get('ContentType', 'application/octet-stream'),
                        'storage': 'wasabi'
                    })
            
            return documents
        except Exception as e:
            logger.error(f"Wasabi list failed for patient {patient_id}: {e}")
            return []

    def delete_document(self, object_key: str) -> bool:
        """Delete from Wasabi"""
        if not self.is_configured(): return False
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=object_key)
            return True
        except Exception as e:
            logger.error(f"Wasabi delete failed: {e}")
            return False

    def get_document_metadata(self, object_key: str) -> Optional[Dict[str, Any]]:
        """Get document metadata"""
        if not self.is_configured(): return None
        try:
            response = self.s3_client.head_object(Bucket=self.bucket_name, Key=object_key)
            return {
                'metadata': response.get('Metadata', {}),
                'content_type': response.get('ContentType'),
                'content_length': response.get('ContentLength'),
                'last_modified': response.get('LastModified').isoformat() if response.get('LastModified') else None,
                'storage': 'wasabi'
            }
        except Exception as e:
            logger.error(f"Wasabi metadata fetch failed: {e}")
            return None

    @staticmethod
    def _get_content_type(filename: str) -> str:
        """Determine content type from filename"""
        ext = filename.lower().split('.')[-1]
        content_types = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'dcm': 'application/dicom',
            'txt': 'text/plain'
        }
        return content_types.get(ext, 'application/octet-stream')
