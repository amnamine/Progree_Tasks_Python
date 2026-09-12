"""
Multi-Intent Router and Nested State Logic Handler.
Routes user goals across structured flows, deterministic rules,
functional dictionary dispatch maps, and fallback channels.
"""

import time
from typing import Dict, Any, Tuple, List, Optional
from nlp_normalizer import NLPNormalizer
from dialogue_trees import DialogueTreeEngine


class IntentRouter:
    """Classifies user intent, maintains session context, and routes to handlers."""

    def __init__(self):
        self.tree_engine = DialogueTreeEngine()

        # Keyword mapping for Intent Classification
        self.intent_keywords = {
            "greeting": ["hello", "hi", "hey", "greetings", "good morning", "good evening", "howdy", "sup", "yo"],
            "farewell": ["bye", "goodbye", "see you", "farewell", "exit", "quit", "cya", "have a nice day"],
            "help": ["help", "menu", "options", "what can you do", "commands", "guide", "features"],
            "tech_support": ["tech support", "technical", "broken", "wifi", "internet", "crash", "error", "troubleshoot", "hardware", "screen", "freeze", "slow pc", "bug"],
            "billing_orders": ["billing", "order", "invoice", "receipt", "refund", "subscription", "price", "pricing", "payment", "track order", "cost", "charge"],
            "tech_quiz": ["quiz", "test", "trivia", "game", "challenge", "questions", "exam"],
            "diagnostics": ["diagnostics", "status", "health", "system info", "telemetry", "uptime", "stats", "specs"],
            "feedback": ["feedback", "rate", "review", "opinion", "stars", "survey"],
            "about": ["who are you", "what are you", "author", "creator", "architecture", "version", "about"]
        }

        # Functional Dictionary Dispatch Map for Single-Turn Deterministic Rules
        self.rule_dispatch_map = {
            "greeting": self._rule_greeting,
            "farewell": self._rule_farewell,
            "help": self._rule_help,
            "about": self._rule_about
        }

    # =========================================================================
    # SINGLE-TURN RULE HANDLERS (Dictionary Mapped)
    # =========================================================================
    def _rule_greeting(self, user_text: str, session: Dict[str, Any]) -> Tuple[str, List[str]]:
        msg = (
            "👋 **Hello! Welcome to Nexus Hybrid Assistant.**\n"
            "I am equipped with a **Multi-Intent Rule Engine** combined with **Groq Neural AI**.\n\n"
            "How can I assist you today?"
        )
        pills = ["Technical Support", "Billing & Orders", "Take Tech Quiz", "System Diagnostics", "Ask Groq AI"]
        return msg, pills

    def _rule_farewell(self, user_text: str, session: Dict[str, Any]) -> Tuple[str, List[str]]:
        msg = (
            "🌟 **Thank you for chatting with Nexus!**\n"
            "Have a fantastic day ahead. Feel free to come back whenever you need assistance."
        )
        return msg, ["Start New Session", "Help Menu"]

    def _rule_help(self, user_text: str, session: Dict[str, Any]) -> Tuple[str, List[str]]:
        msg = (
            "📖 **Nexus Capabilities & Navigation Menu**\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "• 🛠️ **Technical Support Wizard:** Step-by-step troubleshooting & ticketing.\n"
            "• 💳 **Billing & E-Commerce:** Order tracking, refund calculator, PDF invoices.\n"
            "• 🧠 **Interactive Tech Quiz:** Test your Python, AI, and IT knowledge.\n"
            "• ⚙️ **Diagnostics & Telemetry:** Real-time bot metrics & engine status.\n"
            "• ⭐ **Feedback & Review:** Rate your session and share feedback.\n"
            "• 🤖 **Ask AI / Open Chat:** Ask any open-ended or coding question to Groq LLM!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            "Type a command, pick a pill below, or ask any question directly!"
        )
        pills = ["Technical Support", "Billing & Orders", "Take Quiz", "Diagnostics", "Give Feedback"]
        return msg, pills

    def _rule_about(self, user_text: str, session: Dict[str, Any]) -> Tuple[str, List[str]]:
        msg = (
            "🤖 **Nexus Hybrid Architecture Overview**\n\n"
            "• **Rule-Based Engine:** Nested `if-elif-else` branches + functional dictionary dispatch.\n"
            "• **NLP Normalizer:** Regex tokenization, contraction expansion, entity extraction.\n"
            "• **State Machine:** Multi-turn conversational trees with session persistence.\n"
            "• **Groq AI Integration:** Ultra-fast cloud LLMs (Llama-3.3 / Qwen / GPT-OSS) for open queries.\n"
            "• **UI Framework:** Custom Styled Dark Luxe Tkinter GUI + Terminal CLI Interface."
        )
        return msg, ["Main Menu", "Help", "Run Diagnostics", "Ask AI"]

    # =========================================================================
    # CORE ROUTING ENGINE
    # =========================================================================
    def route_message(self, user_text: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main routing function executing nested state logic and dispatch maps.
        Returns:
            {
                "response": str,
                "quick_replies": List[str],
                "intent": str,
                "confidence": float,
                "handled_by": str ("rule_tree", "rule_map", "fallback_ai"),
                "tree_completed": bool
            }
        """
        session["total_turns"] = session.get("total_turns", 0) + 1
        active_tree = session.get("active_tree")

        # -------------------------------------------------------------
        # 1. Active Multi-Turn State Tree Continuation
        # -------------------------------------------------------------
        if active_tree:
            # Check if user wants to explicitly break out
            cleaned = NLPNormalizer.clean_text(user_text)
            if cleaned in ["cancel", "exit", "quit", "menu", "restart", "stop"]:
                session["active_tree"] = None
                session["tree_step"] = 0
                session["tree_data"] = {}
                return {
                    "response": "🛑 Flow cancelled. Returned to main conversational router.",
                    "quick_replies": ["Help Menu", "Technical Support", "Billing & Orders", "Ask AI"],
                    "intent": "flow_cancelled",
                    "confidence": 1.0,
                    "handled_by": "rule_tree",
                    "tree_completed": True
                }

            # Continue executing active tree
            resp_text, pills, is_completed = self.tree_engine.execute_tree(active_tree, user_text, session)
            if is_completed:
                session["active_tree"] = None
                session["tree_step"] = 0
                session["tree_data"] = {}

            return {
                "response": resp_text,
                "quick_replies": pills,
                "intent": active_tree,
                "confidence": 1.0,
                "handled_by": "rule_tree",
                "tree_completed": is_completed
            }

        # -------------------------------------------------------------
        # 2. Intent Classification via NLP Normalizer
        # -------------------------------------------------------------
        matched_intent, confidence = NLPNormalizer.match_intent_keywords(user_text, self.intent_keywords)
        session["active_intent"] = matched_intent or "unknown"
        session["intent_confidence"] = confidence

        # -------------------------------------------------------------
        # 3. High-Confidence Multi-Step Tree Triggers
        # -------------------------------------------------------------
        if matched_intent in self.tree_engine.trees and confidence >= 0.20:
            session["active_tree"] = matched_intent
            session["tree_step"] = 0
            session["tree_data"] = {}
            resp_text, pills, is_completed = self.tree_engine.execute_tree(matched_intent, user_text, session)
            if is_completed:
                session["active_tree"] = None

            return {
                "response": resp_text,
                "quick_replies": pills,
                "intent": matched_intent,
                "confidence": confidence,
                "handled_by": "rule_tree",
                "tree_completed": is_completed
            }

        # -------------------------------------------------------------
        # 4. Single-Turn Deterministic Rule Dispatch Map
        # -------------------------------------------------------------
        if matched_intent in self.rule_dispatch_map and confidence >= 0.20:
            handler = self.rule_dispatch_map[matched_intent]
            resp_text, pills = handler(user_text, session)
            return {
                "response": resp_text,
                "quick_replies": pills,
                "intent": matched_intent,
                "confidence": confidence,
                "handled_by": "rule_map",
                "tree_completed": True
            }

        # -------------------------------------------------------------
        # 5. Fallback or Delegation to Groq AI LLM
        # -------------------------------------------------------------
        return {
            "response": None,  # Needs AI / Fallback resolution
            "quick_replies": ["Help Menu", "Technical Support", "Billing", "Ask Groq AI"],
            "intent": matched_intent or "open_query",
            "confidence": confidence,
            "handled_by": "fallback_ai",
            "tree_completed": True
        }
