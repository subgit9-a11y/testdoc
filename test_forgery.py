"""
Tests for PDF Prescription Forgery & Non-Repudiation (Issue #28)
"""
import sys
import os
import unittest
import asyncio
from types import SimpleNamespace
from unittest.mock import patch, MagicMock

sys.path.insert(0, r"c:\Users\SUBHASH\Desktop\astrafinalneed\astra")
os.environ["PRESCRIPTION_SECRET"] = "test-secret"
os.environ["CUSTOM_WA_API_BASE_URL"] = "http://mock"
os.environ["CUSTOM_WA_BEARER_TOKEN"]  = "mock"
os.environ["CUSTOM_WA_VENDOR_UID"]    = "mock"

from app.ayureze_prescription_template import generate_prescription_hash
from app.prescription_pdf_endpoint import verify_prescription

def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

class TestPrescriptionForgery(unittest.TestCase):
    def setUp(self):
        self.mock_rx = SimpleNamespace()
        self.mock_rx.patient = SimpleNamespace(name="John Doe", date="2026-05-21")
        self.mock_rx.doctor = SimpleNamespace(name="Dr. Smith")
        self.mock_rx.prescribed_medicines = [
            {"medicine": "Medicine A", "dose": "1", "schedule": "1-0-1"},
            {"medicine": "Medicine B", "dose": "2", "schedule": "0-1-0"}
        ]
        self.valid_hash = generate_prescription_hash(self.mock_rx)
        self.short_hash = self.valid_hash[:12]

    def test_hash_generation_deterministic(self):
        hash1 = generate_prescription_hash(self.mock_rx)
        hash2 = generate_prescription_hash(self.mock_rx)
        self.assertEqual(hash1, hash2)
        print("  [PASSED] Hash generation is deterministic")

    def test_hash_changes_on_tampering(self):
        # Tamper with the medicine quantity (simulating a patient changing 1 to 10)
        tampered_rx = SimpleNamespace()
        tampered_rx.patient = SimpleNamespace(name="John Doe", date="2026-05-21")
        tampered_rx.doctor = SimpleNamespace(name="Dr. Smith")
        tampered_rx.prescribed_medicines = [
            {"medicine": "Medicine A", "dose": "10", "schedule": "1-0-1"}, # Changed dose!
            {"medicine": "Medicine B", "dose": "2", "schedule": "0-1-0"}
        ]
        tampered_hash = generate_prescription_hash(tampered_rx)
        self.assertNotEqual(self.valid_hash, tampered_hash)
        print("  [PASSED] Hash changes immediately upon data tampering")

    @patch("app.prescription_pdf_endpoint.db_manager")
    @patch("app.prescription_pdf_endpoint.shopify_client")
    def test_verification_endpoint_authentic(self, mock_shopify, mock_db):
        # Simulate DB returning the correct data
        mock_db.is_connected.return_value = True
        mock_db.get_prescription = AsyncMock(return_value={
            "patient_id": "P1",
            "prescribed_at": "2026-05-21T10:00:00Z",
            "doctor_name": "Dr. Smith",
            "prescribed_medicines": [
                {"medicine": "Medicine A", "dose": "1", "schedule": "1-0-1"},
                {"medicine": "Medicine B", "dose": "2", "schedule": "0-1-0"}
            ]
        })
        mock_db.get_patient_profile = AsyncMock(return_value={"name": "John Doe"})

        result = _run(verify_prescription("RX-123", self.short_hash))
        self.assertTrue(result["authentic"])
        self.assertEqual(result["status"], "verified")
        print("  [PASSED] Verification endpoint accepts authentic signature")

    @patch("app.prescription_pdf_endpoint.db_manager")
    @patch("app.prescription_pdf_endpoint.shopify_client")
    def test_verification_endpoint_forgery(self, mock_shopify, mock_db):
        # Simulate DB returning the *original* data
        mock_db.is_connected.return_value = True
        mock_db.get_prescription = AsyncMock(return_value={
            "patient_id": "P1",
            "prescribed_at": "2026-05-21T10:00:00Z",
            "doctor_name": "Dr. Smith",
            "prescribed_medicines": [
                {"medicine": "Medicine A", "dose": "1", "schedule": "1-0-1"}, # Server says 1
                {"medicine": "Medicine B", "dose": "2", "schedule": "0-1-0"}
            ]
        })
        mock_db.get_patient_profile = AsyncMock(return_value={"name": "John Doe"})

        # Patient modified the PDF and generated a fake signature, OR they used the original signature
        # but the pharmacist is checking it against a forged paper document.
        # Wait, if they bring a forged paper document, the QR code still contains the *original* signature.
        # But if they try to forge the signature too, it won't match the server.
        fake_signature = "a1b2c3d4e5f6"
        result = _run(verify_prescription("RX-123", fake_signature))
        
        self.assertFalse(result["authentic"])
        self.assertEqual(result["status"], "forgery_detected")
        print("  [PASSED] Verification endpoint rejects forged/tampered signature")

class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)

if __name__ == "__main__":
    print("=" * 60)
    print("PRESCRIPTION FORGERY TESTS (Issue #28)")
    print("=" * 60)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestPrescriptionForgery)
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if res.wasSuccessful() else 1)
