# 🚀 PROGREE Python Internship — Comprehensive Project Showcase

Welcome to the **Progree Python Internship** repository. This repository encapsulates a suite of production-grade Python projects and automation utilities developed during the internship program. Each task adheres to clean architecture, robust error sanitization, high performance, automated testing, and modern desktop/terminal user interfaces.

---

## 📑 Table of Contents

- [Overview & Objectives](#-overview--objectives)
- [Repository Structure](#-repository-structure)
- [Task Breakdowns](#-task-breakdowns)
  - [Task 1: Professional LinkedIn Announcement](#task-1-professional-linkedin-announcement)
  - [Task 2: Core Algorithmic Fibonacci Generation Module](#task-2-core-algorithmic-fibonacci-generation-module)
  - [Task 3: Automated File Operating & Text-Parsing Script](#task-3-automated-file-operating--text-parsing-script)
  - [Task 4: Mini Project — Multi-Intent Rule-Based & Hybrid AI Chatbot](#task-4-mini-project--multi-intent-rule-based--hybrid-ai-chatbot)
- [Getting Started & Installation](#-getting-started--installation)
- [Testing & Quality Assurance](#-testing--quality-assurance)
- [Tech Stack & Standards](#-tech-stack--standards)

---

## 🎯 Overview & Objectives

The **Progree Python Internship** curriculum is engineered to test and expand core software engineering skills in Python:

| Task | Domain | Key Topics & Deliverables |
| :--- | :--- | :--- |
| **Task 1** | Professional Network | Official Internship Acceptance announcement & networking. |
| **Task 2** | Core Algorithms & Benchmarks | $O(\log n)$ Fibonacci algorithms, input sanitization, `timeit` metrics & Golden Spiral UI. |
| **Task 3** | System Automation & RegEx | Directory organizing, multi-pattern log parser, Master CSV export & background daemon. |
| **Task 4** | Conversational AI & NLP | Multi-intent nested state machines, dictionary dispatch, Groq Cloud LLM & modern Tkinter GUI. |

---

## 📂 Repository Structure

```tree
PROGREE_INTERNSHIP/Python/
│
├── Python Programming Tasks & Instructions.pdf   # Official curriculum specifications
├── README.md                                     # Root project documentation (this file)
│
├── Task 2/                                       # Core Algorithmic Fibonacci Suite
│   ├── fibonacci/                                # Algorithm engine, validators & benchmarks
│   ├── gui/                                      # Modern Tkinter visualizer & spiral canvas
│   ├── tests/                                    # Unit tests for correctness & boundary checks
│   ├── main.py                                   # Dual CLI / GUI launcher
│   └── README.md                                 # Task 2 dedicated documentation
│
├── Task 3/                                       # AutoFile & LogParser Pro Suite
│   ├── core/                                     # File sorter, regex parser, daemon watcher
│   ├── ui/                                       # Dark theme Tkinter suite, telemetry, log terminal
│   ├── sample_unorganized_data/                  # Demo testbed with messy files & raw logs
│   ├── master_logs_export.csv                    # Clean master CSV export artifact
│   ├── main.py                                   # Desktop application orchestrator
│   ├── test_suite.py                             # Automated test suite
│   ├── requirements.txt                          # Dependencies
│   └── README.md                                 # Task 3 dedicated documentation
│
└── Task 4/                                       # Production-Ready Multi-Intent Chatbot
    ├── config.py                                 # Groq API configuration & UI theme tokens
    ├── nlp_normalizer.py                         # Text cleaning, contractions & entity extraction
    ├── dialogue_trees.py                         # Nested state machines (Support, Billing, Quiz, etc.)
    ├── intent_router.py                          # Multi-intent router & dictionary dispatch maps
    ├── groq_engine.py                            # Groq Cloud LLM engine with fallback
    ├── hybrid_chatbot.py                         # Master hybrid controller & session manager
    ├── gui_app.py                                # Luxury Tkinter GUI application
    ├── cli_chatbot.py                            # Terminal interactive conversational loop
    ├── test_chatbot.py                           # Automated test suite
    ├── main.py                                   # Unified CLI/GUI launcher
    ├── requirements.txt                          # Dependencies
    └── README.md                                 # Task 4 dedicated documentation
```

---

## 🛠️ Task Breakdowns

### Task 1: Professional LinkedIn Announcement
- **Objective**: Announce official acceptance into the Progree Python Internship on LinkedIn.
- **Deliverables**:
  - High-resolution copy of the official Internship Offer Letter.
  - Formatted post detailing learning milestones, goals, and technical areas of focus.
  - Tagged **Progree** with professional hashtags (`#pythonprogramming`, `#scripting`, `#software`, `#progree`).

---

### Task 2: Core Algorithmic Fibonacci Generation Module
- **Objective**: High-performance mathematical computing module calculating exact sequence values under variable parameter limits and bounds.
- **Highlights**:
  - **Algorithms**: Fast Doubling ($O(\log n)$), Matrix Exponentiation ($O(\log n)$), Linear Iterative ($O(n)$), Memoized Dynamic Programming ($O(n)$), and Infinite Generator Streams ($O(1)$ space).
  - **Input Sanitization**: Strict input validation checking for negative bounds (`NegativeBoundError`), invalid types (`InvalidInputError`), and inverted bounds (`RangeBoundError`).
  - **Benchmarking**: Built-in statistical `timeit` framework reporting Mean, Min, Max, Standard Deviation, and Ops/sec.
  - **GUI**: Modern dark Tkinter interface featuring an interactive **Golden Ratio Spiral visualizer** and sequence export (CSV/JSON).
- **Run**:
  ```bash
  cd "Task 2"
  python main.py          # Launch GUI
  python main.py --cli    # Launch CLI
  ```

---

### Task 3: Automated File Operating & Text-Parsing Script
- **Objective**: Background automation utility leveraging standard system libraries (`os`, `shutil`, `re`, `pathlib`, `csv`) for directory maintenance and log parsing.
- **Highlights**:
  - **Automated Directory Sorting**: Categorizes files into structured folders (`Documents/`, `Spreadsheets/`, `Images/`, `Logs & Dumps/`, etc.) with collision resolution and 1-click **Undo/Rollback**.
  - **Regex Log Extractor**: Extracts Emails, Transaction IDs (`TXN-XXXX`, Stripe `ch_xxx`), IP Addresses, Timestamps, and Log Levels from messy logs.
  - **Master CSV Exporter**: Generates unified audit tables `[Timestamp, Source_File, Line_Number, Entity_Type, Extracted_Value, Context_Snippet]`.
  - **Background Watcher Daemon**: Non-blocking folder monitor that automatically classifies new incoming files and extracts logs in real-time.
- **Run**:
  ```bash
  cd "Task 3"
  pip install -r requirements.txt
  python main.py          # Launch GUI Automation Suite
  python test_suite.py    # Run Automated Tests
  ```

---

### Task 4: Mini Project — Multi-Intent Rule-Based & Hybrid AI Chatbot
- **Objective**: Advanced conversational agent handling modular conversation flows, nested state logic, and hybrid neural LLM integration.
- **Highlights**:
  - **NLP Normalization**: Contraction expansion, word-boundary scoring, and regex entity extraction (Order IDs, Emails, Amounts).
  - **Modular State Trees**:
    - 🛠️ *Technical Support Wizard*: Interactive multi-turn diagnostics with automatic SLA ticket creation.
    - 💳 *Billing & E-Commerce*: Live tracking, 3% fee deduction refund calculator, and PDF invoice generation.
    - 🧠 *Interactive Tech Quiz*: Stateful 3-question evaluation with live scoring and grading.
    - ⚙️ *Diagnostics & Telemetry*: System metrics, turn counts, and session state monitoring.
  - **Hybrid Engine**: Combines deterministic rules (`if-elif-else` + dictionary maps) with **Groq Cloud LLMs** (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`, etc.) with automatic fallback.
  - **Dual Interfaces**: High-fidelity dark slate Tkinter GUI (with animated typing indicator & quick actions) and a rich terminal CLI loop.
- **Run**:
  ```bash
  cd "Task 4"
  pip install -r requirements.txt
  python main.py          # Launch Tkinter GUI
  python main.py --cli    # Launch Terminal CLI
  python test_chatbot.py  # Run Test Suite
  ```

---

## ⚡ Getting Started & Installation

### Prerequisites
- **Python 3.10+** installed on your system.
- Standard libraries: `os`, `sys`, `re`, `shutil`, `pathlib`, `csv`, `timeit`, `threading`, `tkinter`.

### Setup
Clone the repository and install dependencies for tasks that utilize external styling or network utilities:

```bash
# Clone the repository
git clone <repository-url>
cd PROGREE_INTERNSHIP/Python

# Install Task 3 requirements
pip install -r "Task 3/requirements.txt"

# Install Task 4 requirements
pip install -r "Task 4/requirements.txt"
```

---

## 🧪 Testing & Quality Assurance

Each task includes comprehensive automated test suites to ensure edge-case reliability and correctness:

```bash
# Test Task 2 (Fibonacci & Sanitization)
python -m unittest discover "Task 2/tests" -v

# Test Task 3 (File Sorting & RegEx Extraction)
python "Task 3/test_suite.py"

# Test Task 4 (NLP Normalizer & Dialogue State Trees)
python "Task 4/test_chatbot.py"
```

---

## 💻 Tech Stack & Standards

- **Core Language**: Python 3.10+
- **Standard Libraries**: `os`, `shutil`, `pathlib`, `re`, `csv`, `timeit`, `unittest`, `threading`, `dataclasses`, `urllib`
- **User Interfaces**: Python `tkinter` (custom themed components, glassmorphism palettes, canvas rendering, responsive layouts)
- **AI & Cloud Inference**: Groq Cloud API (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`, `openai/gpt-oss-20b`)
- **Coding Standards**: PEP 8 compliant, type annotations, modular object-oriented architecture, and complete exception handling.

---

## 📜 License & Acknowledgments

Developed as part of the **Progree Python Programming Internship Program**. Special thanks to the Progree team and mentors for the structured curriculum and comprehensive project guidelines.
