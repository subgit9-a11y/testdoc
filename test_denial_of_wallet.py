"""
Test Denial of Wallet Protection (Token Budget Monitor)
"""
import sys
import os
import unittest
import asyncio
from unittest.mock import AsyncMock, patch

sys.path.insert(0, r"c:\Users\SUBHASH\Desktop\astrafinalneed\astra")
os.environ["CUSTOM_WA_API_BASE_URL"] = "http://mock"
os.environ["CUSTOM_WA_BEARER_TOKEN"] = "mock"
os.environ["CUSTOM_WA_VENDOR_UID"] = "mock"

from app.companion_api_enhanced import chat_enhanced, ChatRequest
from app.redis_cache import redis_cache
from app.companion_redis_manager import redis_companion_manager

def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)

class TestDenialOfWalletProtection(unittest.TestCase):
    def setUp(self):
        self.journey_id = "test_journey_123"
        import uuid
        self.user_id = f"hacker_user_{uuid.uuid4().hex[:8]}"
        
        # Setup mock journey
        self.mock_journey = {
            "id": self.journey_id,
            "user_id": self.user_id,
            "status": "active",
            "metadata": {}
        }
        
    @patch("app.companion_api.analyze_safety")
    @patch("app.companion_api.monitor_intent_decay")
    @patch("app.companion_api_enhanced.redis_companion_manager.get_journey")
    @patch("app.astra.routes.pipeline_instance")
    def test_token_budget_monitor(self, mock_pipeline, mock_get_journey, mock_intent, mock_safety):
        # 1. Setup mocks
        mock_get_journey.return_value = self.mock_journey
        mock_safety.return_value = {"is_safe": True, "reason": None}
        mock_intent.return_value = {"is_locked": False, "steer_instruction": "", "metadata": {}}
        
        # Simulate an LLM response that uses 1500 tokens
        mock_pipeline.run = AsyncMock(return_value={
            "response": "Here is a normal response.",
            "language": "en",
            "metadata": {"tokens_used": 1500}
        })
        
        req = ChatRequest(journey_id=self.journey_id, message="Hello AI")
        
        # 2. First request: 1500 tokens. Should pass.
        resp1 = _run(chat_enhanced(req, current_user=self.user_id))
        self.assertTrue(resp1.success)
        self.assertNotIn("ACCOUNT FROZEN", resp1.response)
        print("  [PASSED] Request 1: Allowed (Under 2000 token budget)")
        
        # 3. Second request: Another 1500 tokens. Total = 3000 tokens in the hour.
        # This should trigger the freeze condition during execution, returning the freeze message immediately
        # instead of the standard pipeline response.
        resp2 = _run(chat_enhanced(req, current_user=self.user_id))
        self.assertTrue(resp2.success)
        self.assertIn("ACCOUNT FROZEN", resp2.response)
        self.assertTrue(resp2.metadata.get("account_frozen"))
        print("  [PASSED] Request 2: Blocked + Frozen (Exceeded 2000 tokens)")
        
        # 4. Third request: The account is now frozen. Even before evaluating the pipeline,
        # the system should immediately block it based on the Redis 'frozen' flag.
        mock_pipeline.run.reset_mock()
        resp3 = _run(chat_enhanced(req, current_user=self.user_id))
        self.assertTrue(resp3.success)
        self.assertIn("ACCOUNT FROZEN", resp3.response)
        mock_pipeline.run.assert_not_called()
        print("  [PASSED] Request 3: Blocked instantly without hitting AI (Account remains frozen)")

if __name__ == "__main__":
    print("=" * 60)
    print("DENIAL OF WALLET PROTECTION TESTS (Issue #31)")
    print("=" * 60)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestDenialOfWalletProtection)
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if res.wasSuccessful() else 1)
