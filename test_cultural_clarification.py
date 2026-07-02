"""
Test Cultural Clarification Protocol
"""
import sys
import os
import unittest

sys.path.insert(0, r"c:\Users\SUBHASH\Desktop\astrafinalneed\astra")

from app.astra.system_prompt_builder import prompt_builder

class TestCulturalClarificationProtocol(unittest.TestCase):
    def test_cultural_clarification_in_prompt(self):
        prompt = prompt_builder.build_core_prompt(channel="app")
        
        self.assertIn("Cultural Clarification Protocol", prompt, "Protocol header is missing from system prompt")
        self.assertIn("idioms", prompt.lower(), "Keyword 'idioms' is missing")
        self.assertIn("clarifying question", prompt.lower(), "Instruction to ask clarifying question is missing")
        
        print("  [PASSED] Cultural Clarification Protocol is successfully embedded in the Astra System Prompt.")

if __name__ == "__main__":
    print("=" * 60)
    print("CULTURAL CLARIFICATION PROTOCOL TESTS (Issue #34)")
    print("=" * 60)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCulturalClarificationProtocol)
    res = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if res.wasSuccessful() else 1)
