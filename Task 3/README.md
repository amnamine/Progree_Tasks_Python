# ⚡ AutoFile & LogParser Pro — Desktop Automation Suite

> **Task 3: Automated File Operating & Text-Parsing Script**  
> A high-performance Python automation utility & Tkinter GUI for managing local directories, sorting messy files by extension, parsing flat server logs with regular expressions, and logging extracted entities to a clean Master CSV.

---

## 🌟 Key Highlights & Features

### 1. 🗂️ Automated File Organizer
- **Intelligent Extension Classifier**: Automatically categorizes files into clean directory structures (`Documents/`, `Spreadsheets/`, `Images/`, `Audio/`, `Video/`, `Archives/`, `Logs & Dumps/`, `Code & Scripts/`, `Data & Config/`, `Executables/`, `Others/`).
- **Dry-Run Preview Simulation**: Inspect exactly where every file will be moved before performing any actual disk modifications.
- **Collision Resolution Modes**: Supports `Auto-Rename (_1, _2)`, `Overwrite`, and `Skip` duplicate policies.
- **Full Undo Engine**: Complete rollback stack to restore organized files back to their exact original locations.

### 2. ⚡ Regex Text Parsing & Extraction Engine
- **Robust Regex Matchers**: High-speed extraction for:
  - **Emails**: Identifies user accounts and customer addresses.
  - **Transaction IDs**: Matches `TXN-XXXX`, `TRX-XXXX`, `ORD-XXXX`, `INV-XXXX`, Stripe charge tokens (`ch_xxx`, `pi_xxx`), and UUIDs.
  - **IPv4 & IPv6 Addresses**: Server IPs, proxy origins, and client endpoints.
  - **Timestamps / Dates**: ISO-8601, Apache, and custom datetime formats.
  - **Log Levels**: `DEBUG`, `INFO`, `WARN`, `ERROR`, `CRITICAL`, `FATAL`.
  - **Phone Numbers, Monetary Amounts ($/€/£), & Web URLs**.
- **Dynamic Custom Regex Builder**: Add and test your own regex patterns live in the UI.

### 3. 📑 Clean Master CSV Logging
- Exports structured records with standardized schema:
  `[Timestamp, Source_File, Line_Number, Entity_Type, Extracted_Value, Context_Snippet]`
- Interactive table inspector with live column search and 1-click external viewer launch (Excel / default CSV app).

### 4. ⚙️ Multi-Threaded Background Daemon
- Continuous background folder monitor polling at configurable intervals (1s to 60s).
- Non-blocking UI with live status pulses, automated sorting of new incoming files, and real-time log ingestion into Master CSV.

### 5. 🧪 1-Click Automated Test Dumps & Testing Lab
- **Every Tab Features a Dedicated 1-Click Test Dump Button**:
  - **🗂️ File Organizer**: `🧪 Quick Auto-Test Dump` automatically generates messy test files, performs dry-run preview, and sorts into category subdirectories with live progress and undo history.
  - **⚡ Regex Log Parser**: `🧪 Quick Auto-Test Dump` generates rich test log streams, extracts all emails, transaction IDs, IPs, and timestamps, and streams them cleanly into Master CSV.
  - **⚙️ Background Daemon**: `🧪 Live Ingest Test Dump` starts the daemon and drops live files and logs into the monitored inbox to demonstrate real-time auto-sorting and parsing.
  - **📑 Master CSV Explorer**: `🧪 Quick Test & Load Dump` creates and reloads structured test records with instant deduplication and search filtering.
  - **🧪 Test Data Lab & Sidebar**: `🚀 1-Click All-Features Test` and `🚀 Run Full Test Suite Dump (UnitTests)` execute end-to-end pipeline verifications and unit test assertions with real-time logs in the live terminal.

---

## 🏗️ Project Architecture

```
Task 3/
├── core/
│   ├── __init__.py
│   ├── file_organizer.py    # Directory sorting, extension categorizer, collision handler & undo engine
│   ├── text_parser.py       # High-speed regex parser & clean Master CSV exporter
│   ├── watcher.py           # Background automation daemon & real-time folder monitor
│   └── mock_generator.py    # Realistic messy test folder & log file generator
├── ui/
│   ├── __init__.py
│   ├── theme.py             # Curated dark/light theme, color tokens, and fonts
│   ├── components/
│   │   ├── __init__.py
│   │   ├── stat_card.py     # Animated metric cards with glowing indicators
│   │   ├── log_terminal.py  # Rich streaming console with color-coded syntax tags
│   │   └── toast.py         # Smooth animated toast notifications
│   └── views/
│       ├── __init__.py
│       ├── organizer_view.py # File sorting controls, dry-run & batch organize
│       ├── parser_view.py    # Regex log extraction, live data table & CSV exporter
│       ├── automation_view.py# Background watcher daemon with live activity monitor
│       ├── master_csv_view.py# Clean master CSV viewer, search, filter & stats
│       └── generator_view.py # 1-Click test data generator
├── main.py                  # Main application orchestrator & sidebar navigation
├── test_suite.py            # Unit & integration automated test suite
├── requirements.txt         # Project dependencies
└── README.md                # Documentation & usage guide
```

---

## 🚀 Quick Start

### 1. Installation
Ensure Python 3.10+ is installed, then install the lightweight UI dependencies:

```bash
pip install -r requirements.txt
```

### 2. Launching the Application
Run the desktop suite:

```bash
python main.py
```

### 3. Running Automated Tests
Run the automated test suite verifying all file operations, regex extractions, and CSV exports:

```bash
python test_suite.py
```

---

## 💻 Standard Libraries Leveraged
As requested in the project requirements, this application builds upon Python's standard system libraries:
- `os` & `shutil`: Directory management, file moving, tree traversal, collision handling.
- `re`: Regular expressions engine for token extraction and pattern validation.
- `pathlib`: Clean, cross-platform path manipulation.
- `csv`: Structured Master CSV generation and streaming append operations.
- `threading` & `time`: Non-blocking background worker daemon and polling scheduler.
