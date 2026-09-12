# TASK 4: Production-Ready Multi-Intent Rule-Based & Hybrid AI Chatbot

## 📌 Project Overview
Nexus AI is a high-performance, hybrid conversational assistant that combines deterministic, multi-intent, nested rule-based flows (`if-elif-else` structures combined with functional dictionary dispatch maps) with Groq Cloud Neural LLMs (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`, `openai/gpt-oss-20b`, etc.).

It provides both an **Ultra-Modern Tkinter GUI** and a **Rich Interactive Terminal (CLI) loop**.

---

## 🚀 Key Features

### 1. NLP Normalization Pipeline (`nlp_normalizer.py`)
- **Contraction Expansion**: Expands contractions (e.g., `can't` → `cannot`, `it's` → `it is`).
- **Text Cleaning**: Case normalization, regex cleaning, whitespace deduplication.
- **Entity Extraction**: Automatic regex parsing for **Order IDs** (`#ORD-1234`), **Emails**, **Phone Numbers**, and **Monetary Amounts** (`$75.00`).
- **Word-Boundary Intent Matching**: Scored keyword evaluation with whole-word boundary matching.

### 2. Nested State Trees & Modular Flows (`dialogue_trees.py`)
- 🛠️ **Technical Support Wizard**: Multi-turn troubleshooting flow (Hardware, Network, OS, Crashes) with automatic SLA support ticket creation.
- 💳 **Billing & E-Commerce Center**: Order tracking, 3% fee deduction refund calculator, and PDF invoice email dispatch.
- 🧠 **Interactive Tech Quiz**: Stateful 3-question evaluation with live scoring, answer feedback, and grade report.
- ⚙️ **System Diagnostics**: Telemetry reporting, OS runtime metrics, response latency, and turn counters.
- ⭐ **User Feedback & Sentiment Analysis**: 1-5 Star rating recorder and sentiment logging.

### 3. Groq Cloud Neural Engine (`groq_engine.py`)
- Hardcoded Groq API key with direct zero-dependency `urllib` client.
- Dynamic model switching: `openai/gpt-oss-120b`, `qwen/qwen3.8-27b`, `openai/gpt-oss-20b`, `qwen/qwen3.6-27b`, `allam-2-7b`.
- Intelligent reasoning tag stripper (cleans `<think>...</think>` internal blocks).
- Graceful offline fallback.

### 4. Triple Execution Modes
1. 🌟 **Smart Hybrid Mode**: Deterministic rules execute structured tasks; Groq LLM answers open-ended, complex, and coding queries.
2. ⚡ **Pure Rule-Based Mode**: Strict `if-elif-else` + dictionary routing with deterministic suggestion fallback.
3. 🤖 **Pure Groq AI Mode**: Direct cloud neural inference for all queries.

### 5. Ultra-Modern Tkinter Interface (`gui_app.py`)
- **Luxury Dark Slate & Indigo Theme** with glowing accents and responsive layouts.
- **Rich Message Cards**: User & Bot avatars, role tags, timestamps, dynamic wrapping, and single-click copy buttons.
- **Real-Time Animated Typing Indicator**: Wave dot animation while waiting for async LLM completions.
- **Dynamic Quick Action Pills**: Interactive suggested replies that change with conversational context.
- **Live Session Telemetry Sidebar**: Live tracking of detected intent, confidence %, active tree, and interaction turns.
- **Tools**: Conversation Search bar, Chat History Export (Markdown / JSON / TXT), Reset session, and Sound FX.

---

## 💻 How to Run

### 1. Launch the Modern Tkinter GUI:
```bash
python main.py
```
*(or run `python gui_app.py`)*

### 2. Launch the Rich Terminal (CLI) Agent:
```bash
python main.py --cli
```
*(or run `python cli_chatbot.py`)*

### 3. Run Automated Tests:
```bash
python test_chatbot.py
```

---

## 📂 Project Architecture
```
Task 4/
│
├── config.py             # Groq API configuration, models, UI theme tokens
├── nlp_normalizer.py     # Contractions, text cleaning, regex entity extraction
├── dialogue_trees.py     # Nested state machines (Support, Billing, Quiz, Diagnostics)
├── intent_router.py      # Multi-intent classifier & functional dispatch map
├── groq_engine.py        # Groq Cloud LLM integration with fallback
├── hybrid_chatbot.py     # Master controller & session manager
├── gui_app.py            # Luxury Tkinter GUI application
├── cli_chatbot.py        # Rich terminal conversational application loop
├── main.py               # Unified CLI/GUI launcher
├── test_chatbot.py       # Automated unit test suite
└── README.md             # Documentation & Guide
```
