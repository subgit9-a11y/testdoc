"""
Automated Prescription Service (Supabase Powered)
Orchestrates post-prescription workflow using Supabase for all data.
"""

import logging
import uuid
import tempfile
import os
from datetime import datetime, timezone
from typing import Optional, Dict, List, Any

from app.database import db_manager
from app.shopify_models import PrescriptionRequest
from app.shopify_client import shopify_client
from app.prescription_pdf_service import prescription_pdf_service
from app.storage_factory import storage_client
from app.medicine_reminders.reminder_engine import ReminderEngine

logger = logging.getLogger(__name__)

reminder_engine = ReminderEngine()

# Handle WhatsApp Client Import Safely
try:
    from app.medicine_reminders.custom_whatsapp_client import CustomWhatsAppClient as MetaWhatsAppClient
    whatsapp_client = MetaWhatsAppClient()
except:
    class MockWhatsAppClient:
        async def send_text_message(self, *args, **kwargs): return {"success": True}
    whatsapp_client = MockWhatsAppClient()

class AutomatedPrescriptionService:
    async def process_prescription(
        self, 
        prescription_data: PrescriptionRequest,
        doctor_id: str,
        patient_id: str
    ) -> Dict[str, Any]:
        """
        Main entry point using Supabase as primary DB.
        """
        results = {
            "success": False,
            "prescription_id": None,
            "shopify_order": None,
            "pdf_url": None,
            "errors": []
        }

        try:
            # 1. Generate unique Prescription ID
            prescription_id = f"PRES-{uuid.uuid4().hex[:8].upper()}"
            results["prescription_id"] = prescription_id

            # 2. Create Shopify Draft Order
            shopify_res = None
            try:
                shopify_res = shopify_client.create_draft_order(prescription_data)
                results["shopify_order"] = {
                    "draft_order_id": shopify_res.draft_order_id,
                    "invoice_url": shopify_res.invoice_url
                }
            except Exception as e:
                logger.error(f"Shopify error: {e}")
                results["errors"].append(f"Shopify Error: {str(e)}")

            # 3. Save to Supabase
            # Prepare main record - FIXED: Removing non-existent columns to match real schema
            # Storing extra info in notes
            extra_info = ""
            if shopify_res:
                extra_info = f"\n[Shopify Order: {shopify_res.draft_order_id}]\n[Invoice: {shopify_res.invoice_url}]\n[Price: {shopify_res.total_price}]"

            record_data = {
                "prescription_id": prescription_id,
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "diagnosis": prescription_data.diagnosis,
                "notes": (prescription_data.doctor_notes or "") + extra_info,
                "status": 'created',
                "prescribed_at": datetime.now(timezone.utc).isoformat()
            }
            
            # Prepare medicines
            medicines = []
            for item in prescription_data.prescriptions:
                medicines.append({
                    "medicine_name": item.medicine,
                    "quantity": item.quantity,
                    "dose": item.dose,
                    "schedule": item.schedule,
                    "timing": item.timing,
                    "duration": item.duration or "7 days",
                    "instructions": item.instructions or ""
                })
            
            await db_manager.create_prescription(record_data, medicines)

            # 4. PDF & Storage
            pdf_data = None
            try:
                pdf_data = prescription_pdf_service.generate_prescription_pdf(prescription_data)
                if pdf_data and storage_client:
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                        tmp.write(pdf_data)
                        tmp_path = tmp.name
                    
                    try:
                        storage_key = storage_client.upload_document(
                            file_path=tmp_path,
                            patient_id=patient_id,
                            doc_type='prescription',
                            metadata={'prescription_id': prescription_id}
                        )
                        
                        if storage_key:
                            file_size = os.path.getsize(tmp_path)
                            results["pdf_url"] = storage_client.generate_download_url(storage_key)
                            # Log document in Supabase
                            await db_manager.create_document_record({
                                "document_id": str(uuid.uuid4()),
                                "patient_id": patient_id,
                                "doc_type": 'prescription',
                                "original_filename": f"Prescription_{prescription_id}.pdf",
                                "file_size": file_size, # FIXED: Added Not-Null field
                                "storj_object_key": storage_key, # Key in Wasabi
                                "storage_provider": "wasabi",
                                "bucket": storage_client.bucket_name, # Audit trail
                                "file_key": storage_key, # Redundant but for schema compatibility
                                "related_prescription_id": prescription_id
                            })
                    finally:
                        if os.path.exists(tmp_path): os.remove(tmp_path)
            except Exception as e:
                logger.error(f"Storage flow failed: {e}")

            # 5. Medicine Reminders (Automatic Schedule Creation)
            try:
                await reminder_engine.create_medicine_schedules_from_prescription(prescription_id)
                results["reminders_created"] = True
            except Exception as e:
                logger.error(f"Reminder creation failed: {e}")

            # 6. WhatsApp Patient Patient Outreach
            if shopify_res and shopify_res.invoice_url:
                try:
                    patient = await db_manager.get_patient_profile(patient_id)
                    phone = (patient.get("phone") if patient else prescription_data.patient.contact) or ""
                    
                    if phone:
                        # 🌿 Premium WhatsApp Message
                        msg = f"🌿 *AyurEze Consultation Complete*\n\n" \
                             f"Hello {prescription_data.patient.name or 'Patient'},\n" \
                             f"Your consultation is complete. Here is your wellness plan:\n\n" \
                             f"📋 *Diagnosis:* {prescription_data.diagnosis}\n" \
                             f"📄 *View Prescription:* {results['pdf_url']}\n" \
                             f"🛒 *Pharmacy Order:* {shopify_res.invoice_url}\n\n" \
                             f"_We've also set up automatic medicine reminders for you!_ ⏰\n" \
                             f"Take care, \n*AyurEze Healthcare*"
                        
                        await whatsapp_client.send_text_message(phone, msg)
                except Exception as e:
                    logger.error(f"WhatsApp outreach failed: {e}")

            # 7. Email Outreach
            if pdf_data:
                try:
                    patient = await db_manager.get_patient_profile(patient_id)
                    patient_email = (patient.get("email") if patient else prescription_data.patient.contact) or ""
                    
                    if patient_email and '@' in patient_email:
                        logger.info(f"📧 Sending official prescription email to {patient_email}")
                        email_res = prescription_pdf_service.send_prescription_email(
                            prescription=prescription_data,
                            pdf_data=pdf_data,
                            patient_email=patient_email
                        )
                        results["email_sent"] = email_res.get("email_sent", False)
                    else:
                        logger.warning(f"Skipping email for {prescription_id} - no valid email found")
                except Exception as e:
                    logger.error(f"Email outreach failed: {e}")
                    results["errors"].append(f"Email Error: {str(e)}")

            results["success"] = True
            return results

        except Exception as e:
            logger.error(f"Critical error: {e}")
            results["errors"].append(str(e))
            return results

automated_prescription_service = AutomatedPrescriptionService()
