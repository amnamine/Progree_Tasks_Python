"""
Log Text Parser & Regex Extraction View Tab.
Parses flat logs, extracts regex patterns (emails, transaction IDs, IPs, timestamps, etc.),
provides live data exploration, and logs output to a clean Master CSV.
"""

import threading
from tkinter import filedialog, ttk
import customtkinter as ctk
from pathlib import Path
from typing import List

from ui.theme import Theme
from ui.components.stat_card import StatCard
from ui.components.toast import show_toast
from core.text_parser import TextParserEngine, ExtractedEntity, DEFAULT_REGEX_PATTERNS
from core.mock_generator import generate_log_line


class ParserView(ctk.CTkFrame):
    def __init__(self, master, parser: TextParserEngine, log_terminal, on_export_callback=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.parser = parser
        self.log_terminal = log_terminal
        self.on_export_callback = on_export_callback

        self.target_path_var = ctk.StringVar(value="")
        self.master_csv_var = ctk.StringVar(value=str(Path.cwd() / "master_logs_export.csv"))
        self.search_filter_var = ctk.StringVar(value="")
        self.pattern_checkbox_vars = {}
        self.current_entities: List[ExtractedEntity] = []

        self._build_ui()

    def _build_ui(self):
        # Top Metric Stat Cards
        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(fill="x", padx=16, pady=(12, 8))

        self.card_matches = StatCard(stats_row, "Extracted Entities", "0", "⚡", Theme.ACCENT_CYAN, "Total regex matches")
        self.card_matches.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.card_emails = StatCard(stats_row, "Emails & Accounts", "0", "✉️", Theme.ACCENT_PRIMARY, "Identified users")
        self.card_emails.pack(side="left", fill="x", expand=True, padx=4)

        self.card_txns = StatCard(stats_row, "Transaction IDs", "0", "💳", Theme.ACCENT_EMERALD, "Orders & payments")
        self.card_txns.pack(side="left", fill="x", expand=True, padx=(8, 0))

        # Main Control Card
        control_card = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MEDIUM, border_width=1, border_color=Theme.BORDER_SUBTLE)
        control_card.pack(fill="x", padx=16, pady=8)

        # Source Log Picker
        src_row = ctk.CTkFrame(control_card, fg_color="transparent")
        src_row.pack(fill="x", padx=16, pady=(12, 8))

        lbl_src = ctk.CTkLabel(src_row, text="Target Flat Log File or Logs Folder:", font=Theme.get_font(12, "bold"), text_color=Theme.TEXT_MAIN)
        lbl_src.pack(anchor="w", pady=(0, 4))

        picker_box = ctk.CTkFrame(src_row, fg_color="transparent")
        picker_box.pack(fill="x")

        self.path_entry = ctk.CTkEntry(
            picker_box,
            textvariable=self.target_path_var,
            placeholder_text="Select a .log file, .txt stream, or folder of server logs...",
            font=Theme.get_font(12, "normal"),
            height=36,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER_SUBTLE
        )
        self.path_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        file_btn = ctk.CTkButton(
            picker_box,
            text="📄 Select File",
            font=Theme.get_font(11, "bold"),
            width=100,
            height=36,
            fg_color=Theme.BG_CARD_HOVER,
            hover_color=Theme.ACCENT_PRIMARY,
            command=self._browse_single_file
        )
        file_btn.pack(side="left", padx=(0, 6))

        folder_btn = ctk.CTkButton(
            picker_box,
            text="📁 Select Folder",
            font=Theme.get_font(11, "bold"),
            width=110,
            height=36,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_HOVER,
            command=self._browse_folder
        )
        folder_btn.pack(side="left")

        # Entity Extraction Checkboxes
        patterns_frame = ctk.CTkFrame(control_card, fg_color="transparent")
        patterns_frame.pack(fill="x", padx=16, pady=(0, 8))

        lbl_pat = ctk.CTkLabel(patterns_frame, text="Active Extraction Patterns:", font=Theme.get_font(11, "bold"), text_color=Theme.TEXT_MUTED)
        lbl_pat.pack(anchor="w", pady=(0, 4))

        chips_box = ctk.CTkFrame(patterns_frame, fg_color="transparent")
        chips_box.pack(fill="x")

        # Create checkboxes for all default patterns
        for name in DEFAULT_REGEX_PATTERNS.keys():
            var = ctk.BooleanVar(value=True)
            self.pattern_checkbox_vars[name] = var
            cb = ctk.CTkCheckBox(
                chips_box,
                text=name,
                variable=var,
                font=Theme.get_font(11, "normal"),
                checkbox_height=18,
                checkbox_width=18,
                corner_radius=4,
                fg_color=Theme.ACCENT_PRIMARY,
                hover_color=Theme.ACCENT_HOVER
            )
            cb.pack(side="left", padx=(0, 12), pady=2)

        # Custom Regex Expansion Row
        custom_row = ctk.CTkFrame(control_card, fg_color="transparent")
        custom_row.pack(fill="x", padx=16, pady=(4, 10))

        lbl_cust = ctk.CTkLabel(custom_row, text="Add Custom Regex:", font=Theme.get_font(11, "normal"), text_color=Theme.TEXT_MUTED)
        lbl_cust.pack(side="left", padx=(0, 8))

        self.custom_name_entry = ctk.CTkEntry(
            custom_row,
            placeholder_text="Pattern Name (e.g. OrderNumber)",
            width=180,
            height=30,
            font=Theme.get_font(11, "normal"),
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER_SUBTLE
        )
        self.custom_name_entry.pack(side="left", padx=(0, 8))

        self.custom_regex_entry = ctk.CTkEntry(
            custom_row,
            placeholder_text=r"Regex String (e.g. \bORD-\d{5}\b)",
            height=30,
            font=Theme.get_font(11, "normal", mono=True),
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER_SUBTLE
        )
        self.custom_regex_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        add_regex_btn = ctk.CTkButton(
            custom_row,
            text="+ Add Pattern",
            width=100,
            height=30,
            font=Theme.get_font(11, "bold"),
            fg_color=Theme.BG_CARD_HOVER,
            hover_color=Theme.ACCENT_PURPLE,
            command=self._add_custom_pattern
        )
        add_regex_btn.pack(side="left")

        # Action Buttons & Master CSV Destination
        action_row = ctk.CTkFrame(control_card, fg_color="transparent")
        action_row.pack(fill="x", padx=16, pady=(4, 14))

        self.parse_btn = ctk.CTkButton(
            action_row,
            text="⚡ Extract Regex Entities",
            font=Theme.get_font(12, "bold"),
            height=38,
            fg_color=Theme.ACCENT_CYAN,
            text_color="#0F172A",
            hover_color="#0891B2",
            command=self._run_parsing
        )
        self.parse_btn.pack(side="left", padx=(0, 10))

        self.export_csv_btn = ctk.CTkButton(
            action_row,
            text="💾 Save / Export to Master CSV",
            font=Theme.get_font(12, "bold"),
            height=38,
            fg_color=Theme.ACCENT_EMERALD,
            hover_color="#059669",
            command=self._export_to_master_csv
        )
        self.export_csv_btn.pack(side="left", padx=(0, 10))

        self.test_dump_btn = ctk.CTkButton(
            action_row,
            text="🧪 Quick Auto-Test Dump",
            font=Theme.get_font(12, "bold"),
            height=38,
            fg_color=Theme.ACCENT_PURPLE,
            hover_color="#7C3AED",
            command=self._run_quick_test_dump
        )
        self.test_dump_btn.pack(side="left", padx=(0, 10))

        # Search Bar on right of action row
        search_box = ctk.CTkFrame(action_row, fg_color="transparent")
        search_box.pack(side="right")

        self.search_entry = ctk.CTkEntry(
            search_box,
            textvariable=self.search_filter_var,
            placeholder_text="🔍 Filter results...",
            width=200,
            height=34,
            font=Theme.get_font(11, "normal"),
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER_SUBTLE
        )
        self.search_entry.pack(side="left")
        self.search_filter_var.trace_add("write", lambda *args: self._filter_table())

        # Progress Bar & Status Text
        self.progress_bar = ctk.CTkProgressBar(
            self,
            height=6,
            corner_radius=3,
            progress_color=Theme.ACCENT_CYAN,
            fg_color=Theme.BG_CARD
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=16, pady=(4, 6))

        # Extracted Data Table Frame
        table_container = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MEDIUM, border_width=1, border_color=Theme.BORDER_SUBTLE)
        table_container.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        # Table Header
        tbl_header = ctk.CTkFrame(table_container, fg_color="transparent", height=32)
        tbl_header.pack(fill="x", padx=12, pady=(10, 4))

        lbl_tbl = ctk.CTkLabel(tbl_header, text="Extracted Entities Live Stream", font=Theme.get_font(12, "bold"), text_color=Theme.TEXT_MAIN)
        lbl_tbl.pack(side="left")

        self.tbl_count = ctk.CTkLabel(tbl_header, text="0 records parsed", font=Theme.get_font(11, "normal"), text_color=Theme.TEXT_DIM)
        self.tbl_count.pack(side="right")

        # Treeview styled for modern dark mode
        tree_scroll_y = ctk.CTkScrollbar(table_container)
        tree_scroll_y.pack(side="right", fill="y", padx=(0, 4), pady=(0, 10))

        self.tree = ttk.Treeview(
            table_container,
            columns=("file", "line", "type", "value", "context"),
            show="headings",
            style="Organizer.Treeview",
            yscrollcommand=tree_scroll_y.set
        )
        tree_scroll_y.configure(command=self.tree.yview)

        self.tree.heading("file", text="Source File")
        self.tree.heading("line", text="Line")
        self.tree.heading("type", text="Entity Type")
        self.tree.heading("value", text="Extracted Value")
        self.tree.heading("context", text="Context Snippet")

        self.tree.column("file", width=160, anchor="w")
        self.tree.column("line", width=60, anchor="center")
        self.tree.column("type", width=140, anchor="center")
        self.tree.column("value", width=220, anchor="w")
        self.tree.column("context", width=360, anchor="w")

        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _browse_single_file(self):
        file = filedialog.askopenfilename(
            title="Select Flat Log File",
            filetypes=[("Log & Text Files", "*.log *.txt *.csv *.json *.err *.out"), ("All Files", "*.*")]
        )
        if file:
            self.target_path_var.set(file)

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder of Log Files")
        if folder:
            self.target_path_var.set(folder)

    def set_target_path(self, path_str: str):
        self.target_path_var.set(path_str)

    def _add_custom_pattern(self):
        name = self.custom_name_entry.get().strip()
        regex_str = self.custom_regex_entry.get().strip()
        if not name or not regex_str:
            show_toast(self, "Please enter both pattern name and regex.", "warn")
            return

        success = self.parser.add_custom_pattern(name, regex_str)
        if success:
            self.pattern_checkbox_vars[name] = ctk.BooleanVar(value=True)
            self.log_terminal.log("SUCCESS", f"Registered custom regex pattern: '{name}' -> `{regex_str}`")
            show_toast(self, f"Pattern '{name}' added successfully!", "success")
            self.custom_name_entry.delete(0, "end")
            self.custom_regex_entry.delete(0, "end")
        else:
            show_toast(self, "Invalid regular expression syntax.", "error")

    def _get_active_types(self) -> List[str]:
        return [name for name, var in self.pattern_checkbox_vars.items() if var.get()]

    def _run_parsing(self):
        target = self.target_path_var.get().strip()
        if not target:
            show_toast(self, "Please select a log file or directory.", "warn")
            return

        active_types = self._get_active_types()
        if not active_types:
            show_toast(self, "Please select at least one pattern.", "warn")
            return

        self.parse_btn.configure(state="disabled")

        def worker():
            target_p = Path(target)
            results: List[ExtractedEntity] = []

            def progress(current, total, msg):
                frac = current / total if total > 0 else 0
                self.after(0, lambda: self.progress_bar.set(frac))

            if target_p.is_file():
                self.log_terminal.log("INFO", f"Parsing single file '{target_p.name}'...")
                results = self.parser.parse_file(str(target_p), active_entity_types=active_types)
                self.parser.extracted_records = results
            elif target_p.is_dir():
                results = self.parser.parse_directory(
                    str(target_p),
                    active_entity_types=active_types,
                    progress_callback=progress,
                    log_callback=self.log_terminal.log
                )

            self.current_entities = results

            def finalize():
                self.parse_btn.configure(state="normal")
                self.progress_bar.set(1.0)
                self._update_table(self.current_entities)
                self._update_stats(self.current_entities)
                show_toast(self, f"Extracted {len(results)} entities from logs!", "success")

            self.after(0, finalize)

        threading.Thread(target=worker, daemon=True).start()

    def _update_stats(self, entities: List[ExtractedEntity]):
        stats = self.parser.get_summary_stats(entities)
        self.card_matches.update_value(str(stats["total_matches"]), f"{stats['unique_values_count']} unique values")
        
        emails_count = stats["by_type"].get("Email", 0)
        self.card_emails.update_value(str(emails_count), "User emails parsed")

        txns_count = stats["by_type"].get("Transaction ID", 0)
        self.card_txns.update_value(str(txns_count), "Payment transactions")

    def _update_table(self, entities: List[ExtractedEntity]):
        self.tree.delete(*self.tree.get_children())
        self.tbl_count.configure(text=f"{len(entities)} records displayed")
        for e in entities:
            self.tree.insert("", "end", values=(e.source_file, e.line_number, e.entity_type, e.value, e.context_snippet))

    def _filter_table(self):
        query = self.search_filter_var.get().strip().lower()
        if not query:
            self._update_table(self.current_entities)
            return

        filtered = [
            e for e in self.current_entities
            if query in e.value.lower() or query in e.entity_type.lower() or query in e.source_file.lower() or query in e.context_snippet.lower()
        ]
        self._update_table(filtered)

    def _export_to_master_csv(self):
        if not self.current_entities:
            show_toast(self, "No extracted entities to export.", "warn")
            return

        save_path = filedialog.asksaveasfilename(
            title="Export Clean Master CSV",
            defaultextension=".csv",
            filetypes=[("CSV File", "*.csv"), ("All Files", "*.*")],
            initialfile="master_logs_export.csv"
        )
        if not save_path:
            return

        success, count = self.parser.export_master_csv(
            output_csv_path=save_path,
            entities=self.current_entities,
            append_mode=False,
            log_callback=self.log_terminal.log
        )
        if success:
            show_toast(self, f"Saved {count} records to Master CSV!", "success")
            if self.on_export_callback:
                self.on_export_callback(save_path)

    def _run_quick_test_dump(self):
        """Automated 1-Click Test: Creates realistic server logs, extracts regex entities, and logs to Master CSV."""
        self.log_terminal.log("INFO", "🚀 [AUTO-TEST] Starting automated Regex Log Parser test dump...")
        self.test_dump_btn.configure(state="disabled")

        def worker():
            test_dir = Path.cwd() / "sample_unorganized_data"
            test_dir.mkdir(parents=True, exist_ok=True)
            test_log = test_dir / "quick_audit_stream.log"

            # 1. Generate realistic test log stream
            self.log_terminal.log("INFO", f"1. Generating test log stream with emails, TXN IDs, IPs in '{test_log.name}'...")
            with open(test_log, "w", encoding="utf-8") as f:
                for i in range(35):
                    f.write(generate_log_line(i) + "\n")

            self.after(0, lambda: self.target_path_var.set(str(test_log.resolve())))

            # 2. Execute regex parsing
            active_types = self._get_active_types() or list(DEFAULT_REGEX_PATTERNS.keys())
            self.log_terminal.log("INFO", f"2. Parsing log entities using patterns: {', '.join(active_types)}...")
            results = self.parser.parse_file(str(test_log), active_entity_types=active_types)
            self.current_entities = results

            # 3. Export to Master CSV
            master_csv = Path.cwd() / "master_logs_export.csv"
            self.log_terminal.log("INFO", f"3. Streaming extracted records to Master CSV '{master_csv.name}'...")
            self.parser.export_master_csv(
                str(master_csv),
                entities=results,
                append_mode=True,
                log_callback=self.log_terminal.log
            )

            def finalize():
                self.test_dump_btn.configure(state="normal")
                self.progress_bar.set(1.0)
                self._update_table(self.current_entities)
                self._update_stats(self.current_entities)
                self.log_terminal.log("SUCCESS", f"✅ [AUTO-TEST COMPLETE] Extracted {len(results)} entities from '{test_log.name}' and logged to Master CSV!")
                show_toast(self, f"Auto-Test Done! Extracted {len(results)} entities.", "success")
                if self.on_export_callback:
                    self.on_export_callback(str(master_csv.resolve()))

            self.after(0, finalize)

        threading.Thread(target=worker, daemon=True).start()

