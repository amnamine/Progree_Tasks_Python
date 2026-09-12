"""
Configuration Module for Multi-Intent Rule-Based and Hybrid AI Chatbot.
Hardcodes Groq API key, models, themes, and system settings.
"""

import os

# ==========================================
# GROQ API CONFIGURATION (HARDCODED)
# ==========================================
GROQ_API_KEY = ""
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

# Available Models tested on Groq
AVAILABLE_MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "qwen/qwen3.8-27b",
    "qwen/qwen3.6-27b",
    "allam-2-7b"
]

DEFAULT_MODEL = "openai/gpt-oss-120b"
FALLBACK_MODEL = "qwen/qwen3.8-27b"

# ==========================================
# SYSTEM PROMPT FOR GROQ LLM
# ==========================================
SYSTEM_PROMPT = """You are 'NexusAI', an ultra-intelligent, friendly, and expert assistant.
You work as part of a hybrid conversational AI system that combines rule-based deterministic trees with cutting-edge LLM capabilities.
- Be concise, accurate, helpful, and polite.
- Format code cleanly using markdown code blocks if asked.
- Answer user queries directly and gracefully.
- If the user asks about the bot architecture, explain that it utilizes a hybrid engine with nested if-elif-else rules, dictionary dispatchers, and Groq LLM fallback.
"""

# ==========================================
# UI THEME & DESIGN TOKENS (DARK LUXE PALETTE)
# ==========================================
THEME = {
    "bg_main": "#0f172a",          # Deep slate background
    "bg_sidebar": "#1e293b",       # Card / sidebar background
    "bg_chat": "#0b0f19",          # Darker chat canvas background
    "bg_input": "#1e293b",         # Input bar background
    "bg_card": "#1e293b",          # Metric cards
    
    # Message bubbles
    "user_bubble": "#3b82f6",      # Vivid Indigo/Blue
    "user_bubble_border": "#60a5fa",
    "user_text": "#ffffff",
    
    "bot_bubble": "#1e293b",       # Sleek Slate bubble
    "bot_bubble_border": "#334155",
    "bot_text": "#f1f5f9",
    
    "system_bubble": "#312e81",    # Purple accent
    "system_text": "#c7d2fe",
    
    # Accents & Highlights
    "accent": "#6366f1",           # Indigo accent
    "accent_hover": "#4f46e5",
    "accent_light": "#818cf8",
    "accent_green": "#10b981",     # Success / Active badge
    "accent_amber": "#f59e0b",     # Warning / Rule mode
    "accent_cyan": "#06b6d4",      # Hybrid mode
    "accent_rose": "#f43f5e",      # Reset / Error
    
    # Text colors
    "text_primary": "#f8fafc",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    
    # Borders & Dividers
    "border_color": "#334155",
    "border_highlight": "#475569",
    
    # Fonts
    "font_family": "Segoe UI",
    "font_mono": "Consolas",
}

# Bot Identity
BOT_NAME = "Nexus Hybrid AI"
BOT_VERSION = "4.0.0 Pro"
BOT_TAGLINE = "Multi-Intent Rule Engine + Groq AI Brain"
