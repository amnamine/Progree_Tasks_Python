# 🚀 PROGREE Python Internship — Master Repository & Showcase

Welcome to the **Progree Python Programming Internship** master repository. This repository encapsulates an enterprise-grade suite of algorithmic engines, system automation utilities, and hybrid conversational AI systems engineered with clean modular architectures, robust input sanitization, automated test suites, and high-fidelity desktop & terminal user interfaces.

---

## 📑 Table of Contents

- [Overview & Curriculum](#-overview--curriculum)
- [Repository Architecture](#-repository-architecture)
- [Task Breakdowns](#-task-breakdowns)
  - [Task 1: Professional LinkedIn Announcement](#-task-1-professional-linkedin-announcement)
  - [Task 2: Core Algorithmic Fibonacci Generation & Benchmarking Suite](#-task-2-core-algorithmic-fibonacci-generation--benchmarking-suite)
  - [Task 3: AutoFile & LogParser Pro — Desktop Automation & Text-Parsing Suite](#-task-3-autofile--logparser-pro--desktop-automation--text-parsing-suite)
  - [Task 4: Nexus AI — Multi-Intent Rule-Based & Hybrid AI Chatbot](#-task-4-nexus-ai--multi-intent-rule-based--hybrid-ai-chatbot)
- [⚡ Quick Start & Installation](#-quick-start--installation)
- [🧪 Unified Test & Quality Assurance Suite](#-unified-test--quality-assurance-suite)
- [💻 Tech Stack & Architectural Standards](#-tech-stack--architectural-standards)
- [📜 License & Acknowledgments](#-license--acknowledgments)

---

## 🎯 Overview & Curriculum

The **Progree Python Internship** curriculum is designed to master core software engineering principles, algorithmic computational complexity, system-level automation, regex text extraction, and conversational artificial intelligence:

| Task | Domain | Focus Areas & Key Deliverables |
| :--- | :--- | :--- |
| **Task 1** | Professional Outreach | Official Internship Acceptance announcement, career milestones, and community engagement. |
| **Task 2** | Core Algorithms & Benchmarks | $O(\log n)$ Fibonacci algorithms, custom exception sanitization, `timeit` statistical metrics & Golden Spiral Canvas GUI. |
| **Task 3** | System Automation & RegEx | 10+ category directory sorter with dry-run/undo, regex log entity parser, Master CSV exporter & background watcher daemon. |
| **Task 4** | Conversational AI & NLP | Modular nested state machines, functional dictionary dispatch, Groq Cloud LLM engine & luxury dark Tkinter GUI. |

---

## 📂 Repository Architecture

```tree
PROGREE_INTERNSHIP/Python/
│
├── Python Programming Tasks & Instructions.pdf   # Official curriculum specification
├── README.md                                     # Master repository documentation (this file)
│
├── Task 2/                                       # Core Algorithmic Fibonacci Suite
│   ├── fibonacci/                                # Algorithm module
│   │   ├── algorithms.py                         # Fast Doubling, Matrix Exp, Iterative, DP & Generators
│   │   ├── exceptions.py                         # NegativeBoundError, InvalidInputError, RangeBoundError
│   │   ├── benchmark.py                          # timeit benchmarking framework & ASCII reporter
│   │   └── __init__.py                           # Clean public API exports
│   ├── gui/                                      # Desktop Application
│   │   ├── app.py                                # Multi-tab Tkinter interface & Golden Spiral visualizer
│   │   └── theme.py                              # Dark glassmorphism color palette & design tokens
│   ├── tests/                                    # Automated Unit Tests
│   │   ├── test_algorithms.py                    # Algorithm correctness & Big-Int assertions
│   │   ├── test_sanitization.py                  # Boundary, type & edge-case exception tests
│   │   └── __init__.py
│   ├── main.py                                   # Dual GUI / CLI launcher
│   └── README.md                                 # Task 2 dedicated documentation
│
├── Task 3/                                       # AutoFile & LogParser Pro Suite
│   ├── core/                                     # Automation & Parsing Engines
│   │   ├── file_organizer.py                     # Category sorter, collision policies & undo engine
│   │   ├── text_parser.py                        # High-speed regex parser & clean Master CSV exporter
│   │   ├── watcher.py                            # Multi-threaded folder daemon & real-time monitor
│   │   └── mock_generator.py                     # Realistic messy test folder & log file generator
│   ├── ui/                                       # Desktop User Interface
│   │   ├── theme.py                              # Curated dark/light theme, tokens & typography
│   │   ├── components/                           # Stat cards, animated log terminal, toast notifications
│   │   └── views/                                # Organizer, Parser, Daemon, CSV & Generator tabs
│   ├── sample_unorganized_data/                  # Testbed containing sample messy files & raw logs
│   ├── master_logs_export.csv                    # Clean master CSV export artifact
│   ├── main.py                                   # Desktop application orchestrator & sidebar navigation
│   ├── test_suite.py                             # Unit & integration automated test suite
│   ├── requirements.txt                          # Dependencies
│   └── README.md                                 # Task 3 dedicated documentation
│
└── Task 4/                                       # Nexus AI — Multi-Intent & Hybrid Chatbot
    ├── config.py                                 # Groq API configuration & UI theme design tokens
    ├── nlp_normalizer.py                         # Text cleaner, contraction expander & regex entity extractors
    ├── dialogue_trees.py                         # Nested state machines (Support, Billing, Quiz, Telemetry, Sentiment)
    ├── intent_router.py                          # Multi-intent classifier & functional dictionary dispatch maps
    ├── groq_engine.py                            # Zero-dependency Groq Cloud LLM engine with fallback & think-tag cleaner
    ├── hybrid_chatbot.py                         # Master controller, session telemetry & conversation logger
    ├── gui_app.py                                # Luxury Dark Slate Tkinter GUI with animated typing indicators
    ├── cli_chatbot.py                            # Interactive Rich Terminal loop
    ├── test_chatbot.py                           # Automated test suite
    ├── main.py                                   # Unified GUI/CLI launcher
    ├── requirements.txt                          # Dependencies
    └── README.md                                 # Task 4 dedicated documentation
```

---

## 🛠️ Task Breakdowns

### 📢 Task 1: Professional LinkedIn Announcement
- **Objective**: Announce formal onboarding into the Progree Python Programming Internship.
- **Key Deliverables**:
  - High-resolution copy of the official Internship Offer Letter.
  - Comprehensive post outlining technical focus areas: Advanced Algorithmic Complexity, Standard Library Systems Automation, Desktop GUI Engineering, and Hybrid Conversational AI.
  - Targeted networking outreach tagging **Progree** and leveraging professional hashtags (`#pythonprogramming`, `#scripting`, `#softwaredevelopment`, `#progree`).

---

### 🔢 Task 2: Core Algorithmic Fibonacci Generation & Benchmarking Suite
- **Objective**: Compute exact Fibonacci sequence values under arbitrary parameter bounds with formal asymptotic complexity guarantees and a modern GUI.
- **Algorithmic Implementations**:
  - **Fast Doubling ($\mathcal{O}(\log n)$)**: Arbitrarily large exact integer computation via matrix reduction identities:
    $$F(2k) = F(k) \cdot [2F(k+1) - F(k)], \quad F(2k+1) = F(k+1)^2 + F(k)^2$$
  - **Matrix Exponentiation ($\mathcal{O}(\log n)$)**: Binary exponentiation of $2 \times 2$ matrix $\begin{pmatrix} 1 & 1 \\ 1 & 0 \end{pmatrix}^n$.
  - **Linear Iterative ($\mathcal{O}(n)$)**: Cache-friendly forward sequence generator.
  - **Memoized Dynamic Programming**: Cached recursion for analytical workflows.
  - **Infinite Generator Streams ($\mathcal{O}(1)$ space)**: Lazy sequence evaluation for unbounded data pipelines.
- **Robust Input Sanitization**:
  - `NegativeBoundError`: Rejects negative indices.
  - `InvalidInputError`: Type validation for floats, `None`, booleans, and non-numeric strings.
  - `RangeBoundError`: Enforces valid sequence range constraints ($start \le end$).
- **Benchmarking & UI**:
  - Built-in `timeit` framework computing Mean, Min, Max, Standard Deviation, and Ops/sec.
  - Modern Dark Tkinter GUI featuring an interactive **Golden Ratio Spiral visualizer** ($\varphi \approx 1.6180339887$), BigInt calculator, and JSON/CSV/TXT export.
- **Execution Commands**:
  ```bash
  cd "Task 2"
  python main.py          # Launch Desktop GUI
  python main.py --cli    # Launch CLI Benchmark / Demo
  python -m unittest discover tests -v  # Run Test Suite
  ```

---

### ⚡ Task 3: AutoFile & LogParser Pro — Desktop Automation & Text-Parsing Suite
- **Objective**: High-performance Python automation utility & Tkinter GUI for local file management, directory organization, regex log parsing, and Master CSV auditing.
- **Core Capabilities**:
  - **🗂️ Intelligent File Organizer**:
    - Automatically classifies 10+ file categories (`Documents/`, `Spreadsheets/`, `Images/`, `Audio/`, `Video/`, `Archives/`, `Logs & Dumps/`, `Code & Scripts/`, `Data & Config/`, `Executables/`, `Others/`).
    - **Dry-Run Preview Simulation** to inspect destination paths before disk modifications.
    - Collision policies (`Auto-Rename _1, _2`, `Overwrite`, `Skip`) and full **1-Click Undo/Rollback**.
  - **🔍 High-Speed Regex Parsing Engine**:
    - Extracts **Emails**, **Transaction IDs** (`TXN-XXXX`, `TRX-XXXX`, `ORD-XXXX`, `INV-XXXX`, Stripe `ch_xxx`/`pi_xxx`, UUIDs), **IPv4/IPv6 Addresses**, **Timestamps/Dates**, **Log Levels** (`DEBUG` through `CRITICAL`), **Phone Numbers**, **Monetary Amounts**, and **URLs**.
    - Live interactive custom regex tester and builder.
  - **📑 Master CSV Auditing**:
    - Standardized export schema: `[Timestamp, Source_File, Line_Number, Entity_Type, Extracted_Value, Context_Snippet]`.
    - Live data table viewer with instant column filtering and external spreadsheet launcher.
  - **⚙️ Multi-Threaded Background Daemon**:
    - Non-blocking folder watcher daemon polling at configurable intervals (1s to 60s) with live status pulse.
  - **🧪 1-Click Automated Testing Dumps**:
    - Dedicated test dump generators on every tab and 1-click full automated integration test runner.
- **Execution Commands**:
  ```bash
  cd "Task 3"
  pip install -r requirements.txt
  python main.py          # Launch Desktop Automation Suite
  python test_suite.py    # Run Automated Test Suite
  ```

---

### 🤖 Task 4: Nexus AI — Multi-Intent Rule-Based & Hybrid AI Chatbot
- **Objective**: Production-ready conversational assistant combining deterministic, nested state machines and functional dispatch maps with Groq Cloud Neural LLMs.
- **Core Architecture & Features**:
  - **NLP Normalization Pipeline (`nlp_normalizer.py`)**:
    - Contraction expansion (`can't` → `cannot`), case normalization, and regex entity extraction (Order IDs, Emails, Phone Numbers, Dollar Amounts).
    - Word-boundary token scoring for precise intent recognition.
  - **Nested State Dialogue Trees (`dialogue_trees.py`)**:
    - 🛠️ *Technical Support Wizard*: Multi-turn hardware/OS/network troubleshooting with SLA ticket generation.
    - 💳 *Billing & E-Commerce Center*: Order tracking, 3% refund fee calculator, and PDF invoice dispatch.
    - 🧠 *Interactive Tech Quiz*: Stateful 3-question evaluation with instant scoring and grade report.
    - ⚙️ *System Diagnostics & Telemetry*: Real-time CPU/OS metrics, latency, and turn analytics.
    - ⭐ *User Feedback & Sentiment*: 5-star rating evaluation and sentiment logging.
  - **Groq Cloud Neural Engine (`groq_engine.py`)**:
    - Direct `urllib` client supporting `openai/gpt-oss-120b`, `qwen/qwen3.8-27b`, `openai/gpt-oss-20b`, and `allam-2-7b`.
    - Automatic thinking tag cleaner (`<think>...</think>`) and offline fallback.
  - **Triple Operating Modes**:
    - 🌟 **Smart Hybrid Mode**: Deterministic rules handle structured tasks; Groq LLM answers open-ended questions.
    - ⚡ **Pure Rule-Based Mode**: Strict `if-elif-else` and dictionary dispatch routing.
    - 🤖 **Pure Groq AI Mode**: Full neural inference for all interactions.
  - **Ultra-Modern Tkinter GUI (`gui_app.py`)**:
    - Dark slate & indigo theme with custom avatars, dynamic quick-action pills, animated wave typing indicator, live telemetry sidebar, conversation search, and multi-format export (Markdown/JSON/TXT).
  - **Rich Interactive Terminal CLI (`cli_chatbot.py`)**.
- **Execution Commands**:
  ```bash
  cd "Task 4"
  pip install -r requirements.txt
  python main.py          # Launch Desktop Tkinter GUI
  python main.py --cli    # Launch Interactive Terminal CLI
  python test_chatbot.py  # Run Test Suite
  ```

---

## ⚡ Quick Start & Installation

### 1. Prerequisites
- **Python 3.10+** installed.
- Core standard libraries: `os`, `sys`, `re`, `shutil`, `pathlib`, `csv`, `timeit`, `threading`, `dataclasses`, `urllib`, `tkinter`.

### 2. Clone & Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd PROGREE_INTERNSHIP/Python

# Install dependencies for Task 3
pip install -r "Task 3/requirements.txt"

# Install dependencies for Task 4
pip install -r "Task 4/requirements.txt"
```

---

## 🧪 Unified Test & Quality Assurance Suite

All tasks include comprehensive automated test suites covering algorithm correctness, boundary constraints, regex extractions, and multi-turn state transitions:

```bash
# 1. Run Task 2 Unit Tests (Fibonacci, Sanitization, Complexity)
python -m unittest discover "Task 2/tests" -v

# 2. Run Task 3 Automated Test Suite (File Sorting, RegEx, CSV Logger)
python "Task 3/test_suite.py"

# 3. Run Task 4 Chatbot Test Suite (NLP Normalizer, Dialogue Trees, Intent Router)
python "Task 4/test_chatbot.py"
```

---

## 💻 Tech Stack & Architectural Standards

- **Language & Runtime**: Python 3.10+
- **Architectural Paradigms**: Modular Object-Oriented Design, Functional Dictionary Dispatch Maps, Stateful Finite State Machines (FSM).
- **Desktop GUI Framework**: Python `tkinter` / `ttk` (custom styled components, responsive canvas rendering, dark glassmorphic themes).
- **AI & Cloud Inference**: Groq Cloud API (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`, `openai/gpt-oss-20b`).
- **Standard Library Maximization**: Built predominantly on Python's built-in modules (`os`, `shutil`, `re`, `pathlib`, `csv`, `timeit`, `unittest`, `threading`, `dataclasses`, `urllib`).
- **Code Quality**: Strict PEP 8 compliance, comprehensive type hints, custom exception hierarchies, and clean docstrings.

---

## 📜 License & Acknowledgments

Developed as part of the **Progree Python Programming Internship Program**. Special thanks to the mentors and evaluation team at Progree for the rigorous curriculum and engineering guidelines.
