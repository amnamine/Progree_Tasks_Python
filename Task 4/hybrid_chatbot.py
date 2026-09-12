"""
Hybrid Chatbot Controller.
Coordinates the NLP Normalizer, Intent Router, Stateful Trees,
and Groq Cloud AI Engine with session state management.
"""

import json
import time
from typing import Dict, Any, List, Optional
from config import GROQ_API_KEY, DEFAULT_MODEL
from intent_router import IntentRouter
from groq_engine import GroqAIEngine
from nlp_normalizer import NLPNormalizer


class HybridChatbot:
    """Core controller orchestrating Rule Engine and Groq AI Brain."""

    MODE_HYBRID = "Smart Hybrid (Rules + Groq AI)"
    MODE_RULE_ONLY = "Pure Rule-Based Engine"
    MODE_AI_ONLY = "Pure Groq AI (Neural LLM)"

    def __init__(self, mode: str = MODE_HYBRID, model: str = DEFAULT_MODEL):
        self.mode = mode
        self.intent_router = IntentRouter()
        self.groq_engine = GroqAIEngine(api_key=GROQ_API_KEY, model=model)
        
        # Session State
        self.session: Dict[str, Any] = {
            "session_id": f"sess_{int(time.time())}",
            "active_tree": None,
            "tree_step": 0,
            "tree_data": {},
            "active_intent": "none",
            "intent_confidence": 0.0,
            "total_turns": 0,
            "mode": self.mode,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        # Conversation History
        self.history: List[Dict[str, Any]] = []

    def set_mode(self, new_mode: str):
        """Updates operating mode."""
        self.mode = new_mode
        self.session["mode"] = new_mode

    def set_model(self, model_name: str):
        """Updates Groq LLM model."""
        self.groq_engine.set_model(model_name)

    def reset_session(self):
        """Clears active conversation session state and history."""
        self.session = {
            "session_id": f"sess_{int(time.time())}",
            "active_tree": None,
            "tree_step": 0,
            "tree_data": {},
            "active_intent": "none",
            "intent_confidence": 0.0,
            "total_turns": 0,
            "mode": self.mode,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        self.history = []

    def process_input(self, user_input: str) -> Dict[str, Any]:
        """
        Processes user query through current mode pipeline.
        Returns:
            {
                "response": str,
                "quick_replies": List[str],
                "source": str ("Rule Engine" or "Groq AI LLM"),
                "intent": str,
                "confidence": float,
                "model_used": Optional[str],
                "timestamp": str
            }
        """
        timestamp = time.strftime("%H:%M:%S")
        user_input_clean = user_input.strip()

        if not user_input_clean:
            return {
                "response": "Please enter a message or select an action.",
                "quick_replies": ["Help Menu", "Technical Support", "Billing & Orders", "Ask AI"],
                "source": "System",
                "intent": "empty",
                "confidence": 1.0,
                "model_used": None,
                "timestamp": timestamp
            }

        # Log user message in history
        self.history.append({
            "role": "user",
            "content": user_input_clean,
            "timestamp": timestamp
        })

        # =============================================================
        # PATH A: PURE AI ONLY MODE
        # =============================================================
        if self.mode == self.MODE_AI_ONLY:
            ai_res = self.groq_engine.generate_chat_response(self.history[-10:])
            bot_reply = ai_res["content"]
            result = {
                "response": bot_reply,
                "quick_replies": ["Ask Followup", "Explain More", "Main Menu"],
                "source": f"Groq AI ({ai_res.get('model_used', 'LLM')})",
                "intent": "open_ai_query",
                "confidence": 1.0,
                "model_used": ai_res.get("model_used"),
                "timestamp": timestamp
            }
            self.history.append({"role": "assistant", "content": bot_reply, "timestamp": timestamp})
            return result

        # =============================================================
        # PATH B: PURE RULE-BASED MODE OR HYBRID ROUTING
        # =============================================================
        route_res = self.intent_router.route_message(user_input_clean, self.session)

        # If handled by Rule Tree or Rule Map
        if route_res["handled_by"] in ["rule_tree", "rule_map"]:
            bot_reply = route_res["response"]
            result = {
                "response": bot_reply,
                "quick_replies": route_res["quick_replies"],
                "source": "Rule Engine",
                "intent": route_res["intent"],
                "confidence": route_res["confidence"],
                "model_used": None,
                "timestamp": timestamp
            }
            self.history.append({"role": "assistant", "content": bot_reply, "timestamp": timestamp})
            return result

        # Fallback handling
        if self.mode == self.MODE_RULE_ONLY:
            # Deterministic fallback message for pure rule mode
            fallback_msg = (
                "⚠️ **Rule Engine Fallback:**\n"
                f"I could not map '{user_input_clean}' to a known rule tree or intent.\n\n"
                "💡 *Suggestions:*\n"
                "• Type **help** or **menu** for supported options.\n"
                "• Try keywords: `tech support`, `order`, `refund`, `quiz`, `diagnostics`.\n"
                "• Switch to **Smart Hybrid** or **Pure AI** mode for open conversational chat."
            )
            result = {
                "response": fallback_msg,
                "quick_replies": ["Help Menu", "Technical Support", "Billing & Orders", "Take Quiz"],
                "source": "Rule Fallback",
                "intent": "fallback_unmatched",
                "confidence": route_res["confidence"],
                "model_used": None,
                "timestamp": timestamp
            }
            self.history.append({"role": "assistant", "content": fallback_msg, "timestamp": timestamp})
            return result

        # =============================================================
        # PATH C: SMART HYBRID DELEGATION TO GROQ AI
        # =============================================================
        ai_res = self.groq_engine.generate_chat_response(self.history[-10:])
        bot_reply = ai_res["content"]
        result = {
            "response": bot_reply,
            "quick_replies": ["Technical Support", "Billing", "Ask Followup", "Run Diagnostics"],
            "source": f"Groq AI ({ai_res.get('model_used', 'LLM')})",
            "intent": route_res.get("intent", "open_query"),
            "confidence": route_res.get("confidence", 0.0),
            "model_used": ai_res.get("model_used"),
            "timestamp": timestamp
        }
        self.history.append({"role": "assistant", "content": bot_reply, "timestamp": timestamp})
        return result

    def export_history(self, export_format: str = "json") -> str:
        """Exports conversation history to JSON, Markdown, or Plain Text."""
        if export_format.lower() == "json":
            return json.dumps({
                "session": self.session,
                "history": self.history
            }, indent=2)

        elif export_format.lower() in ["markdown", "md"]:
            md_lines = [
                f"# Conversation Export - {self.session.get('session_id')}",
                f"- **Date:** {self.session.get('created_at')}",
                f"- **Mode:** {self.mode}",
                f"- **Total Turns:** {len(self.history) // 2}\n",
                "## Transcript\n"
            ]
            for msg in self.history:
                role = "👤 **User**" if msg["role"] == "user" else "🤖 **Nexus Assistant**"
                md_lines.append(f"{role} *({msg.get('timestamp')})*:\n{msg['content']}\n")
            return "\n".join(md_lines)

        else:  # plain text
            lines = [f"=== Session Transcript ({self.session.get('created_at')}) ==="]
            for msg in self.history:
                role = "User" if msg["role"] == "user" else "Nexus"
                lines.append(f"[{msg.get('timestamp')}] {role}: {msg['content']}\n")
            return "\n".join(lines)
