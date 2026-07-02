import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from typing import Optional, Dict

logger = logging.getLogger(__name__)

class SmtpEmailService:
    """Official SMTP Email Service for AyurEze Healthcare"""
    
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "mail.ayureze.in")
        self.smtp_port = int(os.getenv("SMTP_PORT", "465"))
        self.smtp_user = os.getenv("SMTP_USER", "no-reply@ayureze.in")
        self.smtp_pass = os.getenv("SMTP_PASS", "Ayureze@369369")
        self.email_from = os.getenv("EMAIL_FROM", "no-reply@ayureze.in")
        
        if not self.smtp_pass:
            logger.warning("SMTP Password not found in environment!")

    def send_prescription_email(
        self,
        recipient_email: str,
        pdf_content: bytes,
        patient_name: str,
        doctor_name: str,
        prescription_id: str = ""
    ) -> Dict:
        """Sends official prescription PDF via SMTP"""
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = f"AyurEze Healthcare <{self.email_from}>"
            msg['To'] = recipient_email
            msg['Subject'] = f"Prescription for {patient_name} - {prescription_id}" if prescription_id else f"Your Prescription from {doctor_name}"

            # Body text
            body = f"""
            Hello {patient_name},

            Thank you for choosing AyurEze Healthcare.
            Your consultation with {doctor_name} is complete.

            Please find your official prescription attached to this email.

            Take care,
            AyurEze Healthcare Team 🌿
            """
            msg.attach(MIMEText(body, 'plain'))

            # Attach PDF
            filename = f"Prescription_{prescription_id}.pdf" if prescription_id else "Prescription.pdf"
            attachment = MIMEApplication(pdf_content, _subtype="pdf")
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)
            msg.attach(attachment)

            # Send via SMTP
            # Use SSL for port 465
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)

            logger.info(f"✅ Official prescription email sent to {recipient_email}")
            return {"success": True, "message": "Email sent successfully"}

        except Exception as e:
            import traceback
            logger.error(f"❌ SMTP Error: {str(e)}")
            logger.error(traceback.format_exc())
            return {"success": False, "error": str(e)}

# Global instance
smtp_email_service = SmtpEmailService()
