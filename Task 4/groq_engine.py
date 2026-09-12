"""
Groq Cloud AI Engine Module.
Direct zero-dependency integration with Groq Cloud LLM endpoints via urllib.
"""

import json
import re
import urllib.request
import urllib.error
from typing import List, Dict, Any, Optional
from config import GROQ_API_KEY, GROQ_API_URL, DEFAULT_MODEL, FALLBACK_MODEL, SYSTEM_PROMPT


class GroqAIEngine:
    """Handles communications with the Groq Cloud API for advanced LLM reasoning."""

    def __init__(self, api_key: str = GROQ_API_KEY, model: str = DEFAULT_MODEL):
        self.api_key = api_key
        self.model = model
        self.system_prompt = SYSTEM_PROMPT

    def set_model(self, model_name: str):
        """Sets active Groq model."""
        self.model = model_name

    def clean_llm_response(self, text: str) -> str:
        """Strips internal thinking/reasoning tags like <think>...</think> if present."""
        if not text:
            return ""
        # Remove <think>...</think> blocks
        cleaned = re.sub(r'<think>[\s\S]*?</think>', '', text)
        return cleaned.strip()

    def generate_chat_response(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        timeout: int = 15
    ) -> Dict[str, Any]:
        """
        Sends conversation history to Groq API and returns response text and metadata.
        Returns:
            {
                "success": bool,
                "content": str,
                "model_used": str,
                "error": Optional[str]
            }
        """
        if not self.api_key or self.api_key == "YOUR_GROQ_API_KEY":
            return {
                "success": False,
                "content": "⚠️ Groq API key is not configured.",
                "model_used": self.model,
                "error": "Missing API Key"
            }

        # Prepare messages payload including system prompt
        formatted_messages = [{"role": "system", "content": self.system_prompt}]
        for msg in messages:
            formatted_messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "NexusAI-Chatbot/4.0 (Windows NT 10.0; Win64; x64)"
        }

        try:
            data_bytes = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(GROQ_API_URL, data=data_bytes, headers=headers)

            with urllib.request.urlopen(req, timeout=timeout) as response:
                res_body = json.loads(response.read().decode("utf-8"))
                choice = res_body["choices"][0]["message"]["content"]
                cleaned_text = self.clean_llm_response(choice)
                return {
                    "success": True,
                    "content": cleaned_text,
                    "model_used": self.model,
                    "error": None
                }

        except urllib.error.HTTPError as http_err:
            error_msg = f"HTTP {http_err.code}: {http_err.reason}"
            try:
                err_json = json.loads(http_err.read().decode("utf-8"))
                if "error" in err_json and "message" in err_json["error"]:
                    error_msg = err_json["error"]["message"]
            except Exception:
                pass

            # Try fallback model if model not found
            if http_err.code == 404 and self.model != FALLBACK_MODEL:
                self.model = FALLBACK_MODEL
                return self.generate_chat_response(messages, temperature, max_tokens, timeout)

            return {
                "success": False,
                "content": f"⚠️ AI Neural Engine Error: {error_msg}",
                "model_used": self.model,
                "error": error_msg
            }

        except Exception as e:
            return {
                "success": False,
                "content": f"⚠️ Network Connection Error: Unable to reach Groq Cloud ({str(e)}).",
                "model_used": self.model,
                "error": str(e)
            }
