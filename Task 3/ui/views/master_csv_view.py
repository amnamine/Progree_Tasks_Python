"""
Master CSV Viewer & Inspector View Tab.
Inspects, searches, and visualizes the generated clean Master CSV output.
"""

import os
import csv
from tkinter import filedialog, ttk
import customtkinter as ctk
from pathlib import Path

from ui.theme import Theme
from ui.components.stat_card import StatCard
from ui.components.toast import show_toast
from core.text_parser import TextParserEngine
from core.mock_generator import generate_log_line


class MasterCsvView(ctk.CTkFrame):
    def __init__(self, master, log_terminal, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.log_terminal = log_terminal
        self.csv_path_var = ctk.StringVar(value=str(Path.cwd() / "master_logs_export.csv"))
        self.search_filter_var = ctk.StringVar(value="")
        self.raw_rows = []

        self._build_ui()

    def _build_ui(self):
        # Top Metrics
        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(fill="x", padx=16, pady=(12, 8))

        self.card_total_rows = StatCard(stats_row, "Total CSV Records", "0", "📑", Theme.ACCENT_PRIMARY, "Logged entities")
        self.card_total_rows.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.card_unique = StatCard(stats_row, "Unique Values", "0", "✨", Theme.ACCENT_EMERALD, "Deduplicated")
        self.card_unique.pack(side="left", fill="x", expand=True, padx=4)

        self.card_files = StatCard(stats_row, "Source Files", "0", "📁", Theme.ACCENT_PURPLE, "Originating files")
        self.card_files.pack(side="left", fill="x", expand=True, padx=(8, 0))

        # Control Card
        control_card = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MEDIUM, border_width=1, border_color=Theme.BORDER_SUBTLE)
        control_card.pack(fill="x", padx=16, pady=8)

        # File Picker Row
        f_row = ctk.CTkFrame(control_card, fg_color="transparent")
        f_row.pack(fill="x", padx=16, pady=(14, 10))

        lbl_f = ctk.CTkLabel(f_row, text="Master CSV File Location:", font=Theme.get_font(12, "bold"), text_color=Theme.TEXT_MAIN)
        lbl_f.pack(anchor="w", pady=(0, 4))

        picker_box = ctk.CTkFrame(f_row, fg_color="transparent")
        picker_box.pack(fill="x")

        self.csv_entry = ctk.CTkEntry(
            picker_box,
            textvariable=self.csv_path_var,
            font=Theme.get_font(12, "normal"),
            height=36,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER_SUBTLE
        )
        self.csv_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_btn = ctk.CTkButton(
            picker_box,
            text="📁 Browse CSV...",
            font=Theme.get_font(11, "bold"),
            width=110,
            height=36,
            fg_color=Theme.BG_CARD_HOVER,
            hover_color=Theme.ACCENT_PRIMARY,
            command=self._browse_csv
        )
        browse_btn.pack(side="left", padx=(0, 6))

        load_btn = ctk.CTkButton(
            picker_box,
            text="🔄 Reload Data",
            font=Theme.get_font(11, "bold"),
            width=110,
            height=36,
            fg_color=Theme.ACCENT_CYAN,
            text_color="#0F172A",
            hover_color="#0891B2",
            command=self.load_csv
        )
        load_btn.pack(side="left")

        # Action & Search Row
        act_row = ctk.CTkFrame(control_card, fg_color="transparent")
        act_row.pack(fill="x", padx=16, pady=(0, 14))

        open_sys_btn = ctk.CTkButton(
            act_row,
            text="📊 Open in System App / Excel",
            font=Theme.get_font(11, "bold"),
            height=34,
            fg_color=Theme.ACCENT_EMERALD,
            hover_color="#059669",
            command=self._open_in_system
        )
        open_sys_btn.pack(side="left", padx=(0, 10))

        self.test_dump_btn = ctk.CTkButton(
            act_row,
            text="🧪 Quick Test & Load Dump",
            font=Theme.get_font(11, "bold"),
            height=34,
            fg_color=Theme.ACCENT_PURPLE,
            hover_color="#7C3AED",
            command=self._run_quick_test_dump
        )
        self.test_dump_btn.pack(side="left", padx=(0, 10))

        # Search Bar on right
        search_box = ctk.CTkFrame(act_row, fg_color="transparent")
        search_box.pack(side="right")

        self.search_entry = ctk.CTkEntry(
            search_box,
            textvariable=self.search_filter_var,
            placeholder_text="🔍 Search Master CSV...",
            width=220,
            height=34,
            font=Theme.get_font(11, "normal"),
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER_SUBTLE
        )
        self.search_entry.pack(side="left")
        self.search_filter_var.trace_add("write", lambda *args: self._filter_table())

        # Table Container
        table_container = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MEDIUM, border_width=1, border_color=Theme.BORDER_SUBTLE)
        table_container.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        # Header
        tbl_header = ctk.CTkFrame(table_container, fg_color="transparent", height=32)
        tbl_header.pack(fill="x", padx=12, pady=(10, 4))

        lbl_tbl = ctk.CTkLabel(tbl_header, text="Standard Master CSV Dataset Content", font=Theme.get_font(12, "bold"), text_color=Theme.TEXT_MAIN)
        lbl_tbl.pack(side="left")

        self.tbl_count = ctk.CTkLabel(tbl_header, text="0 records loaded", font=Theme.get_font(11, "normal"), text_color=Theme.TEXT_DIM)
        self.tbl_count.pack(side="right")

        # Treeview
        tree_scroll_y = ctk.CTkScrollbar(table_container)
        tree_scroll_y.pack(side="right", fill="y", padx=(0, 4), pady=(0, 10))

        self.tree = ttk.Treeview(
            table_container,
            columns=("time", "source", "line", "type", "value", "context"),
            show="headings",
            style="Organizer.Treeview",
            yscrollcommand=tree_scroll_y.set
        )
        tree_scroll_y.configure(command=self.tree.yview)

        self.tree.heading("time", text="Timestamp")
        self.tree.heading("source", text="Source File")
        self.tree.heading("line", text="Line")
        self.tree.heading("type", text="Entity Type")
        self.tree.heading("value", text="Extracted Value")
        self.tree.heading("context", text="Context Snippet")

        self.tree.column("time", width=140, anchor="center")
        self.tree.column("source", width=160, anchor="w")
        self.tree.column("line", width=60, anchor="center")
        self.tree.column("type", width=130, anchor="center")
        self.tree.column("value", width=220, anchor="w")
        self.tree.column("context", width=340, anchor="w")

        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _browse_csv(self):
        file = filedialog.askopenfilename(
            title="Open Master CSV File",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if file:
            self.csv_path_var.set(file)
            self.load_csv()

    def set_csv_path(self, path_str: str):
        self.csv_path_var.set(path_str)
        self.load_csv()

    def load_csv(self):
        target = self.csv_path_var.get().strip()
        if not target or not Path(target).is_file():
            show_toast(self, "Master CSV file not found or not yet generated.", "info")
            return

        self.raw_rows.clear()
        try:
            with open(target, "r", encoding="utf-8", errors="replace") as f:
                reader = csv.reader(f)
                header = next(reader, None)
                for row in reader:
                    if len(row) >= 5:
                        self.raw_rows.append(row)

            self._update_table(self.raw_rows)
            self._update_stats(self.raw_rows)
            show_toast(self, f"Loaded {len(self.raw_rows)} records from Master CSV.", "success")
        except Exception as e:
            self.log_terminal.log("ERROR", f"Failed to load Master CSV: {str(e)}")
            show_toast(self, f"Error: {str(e)}", "error")

    def _update_stats(self, rows):
        total = len(rows)
        self.card_total_rows.update_value(str(total), "CSV rows")
        
        unique_vals = len(set(r[4] for r in rows if len(r) > 4))
        self.card_unique.update_value(str(unique_vals), "Distinct tokens")

        source_files = len(set(r[1] for r in rows if len(r) > 1))
        self.card_files.update_value(str(source_files), "Log sources")

    def _update_table(self, rows):
        self.tree.delete(*self.tree.get_children())
        self.tbl_count.configure(text=f"{len(rows)} records shown")
        for r in rows:
            # Ensure row has 6 values
            t = r[0] if len(r) > 0 else ""
            s = r[1] if len(r) > 1 else ""
            l = r[2] if len(r) > 2 else ""
            tp = r[3] if len(r) > 3 else ""
            v = r[4] if len(r) > 4 else ""
            c = r[5] if len(r) > 5 else ""
            self.tree.insert("", "end", values=(t, s, l, tp, v, c))

    def _filter_table(self):
        q = self.search_filter_var.get().strip().lower()
        if not q:
            self._update_table(self.raw_rows)
            return

        filtered = [r for r in self.raw_rows if any(q in col.lower() for col in r)]
        self._update_table(filtered)

    def _open_in_system(self):
        target = self.csv_path_var.get().strip()
        if not target or not Path(target).is_file():
            show_toast(self, "No CSV file exists to open.", "warn")
            return

        try:
            os.startfile(target)
            show_toast(self, "Opened Master CSV in system viewer.", "success")
        except Exception as e:
            show_toast(self, f"Could not open file: {str(e)}", "error")

    def _run_quick_test_dump(self):
        """Automated 1-Click Test: Creates a rich Master CSV dataset dump and reloads the inspector."""
        self.log_terminal.log("INFO", "🚀 [AUTO-TEST] Generating and loading Master CSV test dataset dump...")
        try:
            csv_path = Path.cwd() / "master_logs_export.csv"
            parser = TextParserEngine()

            # Create a sample log stream
            temp_log = Path.cwd() / "sample_unorganized_data" / "master_csv_sample.log"
            temp_log.parent.mkdir(parents=True, exist_ok=True)
            with open(temp_log, "w", encoding="utf-8") as f:
                for i in range(40):
                    f.write(generate_log_line(i) + "\n")

            entities = parser.parse_file(str(temp_log))
            parser.export_master_csv(
                output_csv_path=str(csv_path),
                entities=entities,
                append_mode=False,
                log_callback=self.log_terminal.log
            )

            self.csv_path_var.set(str(csv_path.resolve()))
            self.load_csv()
            self.log_terminal.log("SUCCESS", f"✅ [AUTO-TEST COMPLETE] Loaded {len(entities)} records into Master CSV Explorer!")
            show_toast(self, f"Auto-Test Done! Loaded {len(entities)} records from Master CSV dump.", "success")
        except Exception as e:
            self.log_terminal.log("ERROR", f"Failed to run Master CSV auto-test: {str(e)}")
            show_toast(self, f"Error: {str(e)}", "error")

