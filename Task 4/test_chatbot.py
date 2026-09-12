"""
Automated Test Suite for Task 4 Multi-Intent Rule-Based and Hybrid AI Chatbot.
"""

import unittest
from nlp_normalizer import NLPNormalizer
from intent_router import IntentRouter
from hybrid_chatbot import HybridChatbot
from groq_engine import GroqAIEngine
from config import GROQ_API_KEY


class TestChatbotSuite(unittest.TestCase):

    def setUp(self):
        self.bot = HybridChatbot()

    def test_nlp_normalization(self):
        # Contraction expansion
        expanded = NLPNormalizer.expand_contractions("I can't connect and it's slow")
        self.assertIn("cannot", expanded)
        self.assertIn("it is", expanded)

        # Clean text
        cleaned = NLPNormalizer.clean_text("Hello... World! How are you?!")
        self.assertEqual(cleaned, "hello world how are you")

        # Entity Extraction
        entities = NLPNormalizer.extract_entities("Refund my $85.50 for order #ORD-9821, email: test@domain.com")
        self.assertEqual(entities["amount"], 85.50)
        self.assertEqual(entities["order_id"], "#ORD-9821")
        self.assertEqual(entities["email"], "test@domain.com")

    def test_rule_based_trees(self):
        # 1. Tech Support Tree flow
        res1 = self.bot.process_input("tech support")
        self.assertIn("Technical Support Wizard", res1["response"])
        self.assertEqual(self.bot.session["active_tree"], "tech_support")

        # Select option 1 (WiFi)
        res2 = self.bot.process_input("1")
        self.assertIn("Network Troubleshooting Steps", res2["response"])

        # Confirm resolved
        res3 = self.bot.process_input("yes")
        self.assertIn("resolved", res3["response"].lower())
        self.assertIsNone(self.bot.session["active_tree"])

    def test_billing_orders_tree(self):
        # 2. Billing flow
        res1 = self.bot.process_input("billing")
        self.assertIn("Billing & E-Commerce Center", res1["response"])

        # Track order
        res2 = self.bot.process_input("1")
        self.assertIn("Order ID", res2["response"])

        res3 = self.bot.process_input("#ORD-5544")
        self.assertIn("ORD-5544", res3["response"])
        self.assertIsNone(self.bot.session["active_tree"])

    def test_pure_rule_fallback(self):
        self.bot.set_mode(HybridChatbot.MODE_RULE_ONLY)
        res = self.bot.process_input("what is the quantum entanglement of photons?")
        self.assertEqual(res["source"], "Rule Fallback")
        self.assertIn("Rule Engine Fallback", res["response"])

    def test_groq_llm_hybrid(self):
        self.bot.set_mode(HybridChatbot.MODE_HYBRID)
        # Open ended query routed to Groq LLM
        res = self.bot.process_input("Write a 1-line Python code to reverse a string")
        self.assertIn("Groq AI", res["source"])
        self.assertTrue(len(res["response"]) > 0)
        print("\nGroq Hybrid LLM Test Output:\n", res["response"])

    def test_export_history(self):
        self.bot.process_input("hello")
        self.bot.process_input("diagnostics")
        json_export = self.bot.export_history("json")
        md_export = self.bot.export_history("markdown")
        self.assertIn("diagnostics", json_export.lower())
        self.assertIn("Nexus", md_export)


if __name__ == "__main__":
    unittest.main()
