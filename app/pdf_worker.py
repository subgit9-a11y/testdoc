"""
Celery Background Worker for PDF Generation
Resolves Issue #39: Python OOM Assassination (The Silent Worker Death)

This worker offloads heavy RAM-intensive PDF generation tasks from the 
main FastAPI thread, preventing the Linux OS from triggering OOM-Killer 
on the web servers when multiple doctors prescribe medicine concurrently.
"""

import os
import logging
import json
from celery import Celery
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

# We use Redis as the Celery Message Broker
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "pdf_worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    # Worker limits to prevent OOM even on the worker side
    worker_concurrency=2,  # Limit parallel PDF generations
    worker_max_tasks_per_child=50 # Restart worker after 50 PDFs to clear memory leaks
)

logger = logging.getLogger(__name__)

@celery_app.task(name="generate_and_upload_pdf", bind=True, max_retries=3)
def generate_and_upload_pdf_task(self, prescription_dict: dict, patient_email: str = None, send_email: bool = False):
    """
    Background task to safely generate a PDF without crashing FastAPI.
    """
    logger.info(f"🚀 Celery Worker started PDF generation for prescription...")
    
    try:
        from app.shopify_models import PrescriptionRequest
        from app.prescription_pdf_service import prescription_pdf_service
        from app.wasabi_client import get_wasabi_client
        
        # 1. Reconstruct the pydantic model from JSON dict
        prescription = PrescriptionRequest(**prescription_dict)
        
        # 2. Heavy RAM operation: Generate PDF
        pdf_data = prescription_pdf_service.generate_prescription_pdf(prescription)
        
        # 3. Upload to Wasabi (as requested by prompt)
        wasabi = get_wasabi_client()
        filename = f"prescriptions/{prescription.patient.patient_id}_{prescription.prescription_id}.pdf"
        
        upload_success = wasabi.upload_file_bytes(
            file_bytes=pdf_data,
            object_name=filename,
            content_type="application/pdf"
        )
        
        if not upload_success:
            logger.error("Failed to upload PDF to Wasabi")
            # Retry mechanism
            raise self.retry(countdown=60)
            
        logger.info(f"✅ Celery Worker completed PDF generation and uploaded to Wasabi: {filename}")
        
        # 4. Email Notification
        if send_email and patient_email:
            try:
                prescription_pdf_service.send_prescription_email(
                    prescription=prescription, 
                    pdf_data=pdf_data,
                    patient_email=patient_email
                )
                logger.info(f"📧 Celery Worker sent prescription email to {patient_email}")
            except Exception as e:
                logger.error(f"Failed to send email from Celery worker: {e}")
        
        return {"status": "success", "filename": filename}
        
    except Exception as e:
        logger.error(f"❌ Celery PDF Task failed: {e}")
        # Retry with exponential backoff on failure
        raise self.retry(exc=e, countdown=2 ** self.request.retries * 60)
