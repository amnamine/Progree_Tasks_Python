"""
Mock Data Generator View Tab.
Creates an instant realistic messy test environment with flat logs and mixed files.
"""

import os
import io
import threading
import unittest
from tkinter import filedialog
import customtkinter as ctk
from pathlib import Path

from ui.theme import Theme
from ui.components.stat_card import StatCard
from ui.components.toast import show_toast
from core.mock_generator import generate_mock_environment


class GeneratorView(ctk.CTkFrame):
    def __init__(self, master, log_terminal, on_folder_generated=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.log_terminal = log_terminal
        self.on_folder_generated = on_folder_generated

        self.gen_dir_var = ctk.StringVar(value=str(Path.cwd() / "sample_unorganized_data"))
        self.num_files_var = ctk.IntVar(value=14)
        self.num_logs_var = ctk.IntVar(value=5)
        self.lines_per_log_var = ctk.IntVar(value=50)

        self._build_ui()

    def _build_ui(self):
        # Top Metrics
        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(fill="x", padx=16, pady=(12, 8))

        self.card_status = StatCard(stats_row, "Test Generator", "READY", "🧪", Theme.ACCENT_PURPLE, "Instant dataset maker")
        self.card_status.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.card_sim_files = StatCard(stats_row, "Files Configured", f"{self.num_files_var.get() + self.num_logs_var.get()}", "📦", Theme.ACCENT_CYAN, "Total files")
        self.card_sim_files.pack(side="left", fill="x", expand=True, padx=4)

        self.card_sim_logs = StatCard(stats_row, "Log Lines", f"{self.num_logs_var.get() * self.lines_per_log_var.get()}", "⚡", Theme.ACCENT_EMERALD, "Simulated log entries")
        self.card_sim_logs.pack(side="left", fill="x", expand=True, padx=(8, 0))

        # Generator Card
        control_card = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MEDIUM, border_width=1, border_color=Theme.BORDER_SUBTLE)
        control_card.pack(fill="x", padx=16, pady=8)

        # Folder destination row
        f_row = ctk.CTkFrame(control_card, fg_color="transparent")
        f_row.pack(fill="x", padx=16, pady=(14, 10))

        lbl_f = ctk.CTkLabel(f_row, text="Target Output Directory for Mock Test Data:", font=Theme.get_font(12, "bold"), text_color=Theme.TEXT_MAIN)
        lbl_f.pack(anchor="w", pady=(0, 4))

        picker_box = ctk.CTkFrame(f_row, fg_color="transparent")
        picker_box.pack(fill="x")

        self.gen_entry = ctk.CTkEntry(
            picker_box,
            textvariable=self.gen_dir_var,
            font=Theme.get_font(12, "normal"),
            height=36,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER_SUBTLE
        )
        self.gen_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_btn = ctk.CTkButton(
            picker_box,
            text="📁 Browse...",
            font=Theme.get_font(11, "bold"),
            width=110,
            height=36,
            fg_color=Theme.BG_CARD_HOVER,
            hover_color=Theme.ACCENT_PRIMARY,
            command=self._browse_folder
        )
        browse_btn.pack(side="left")

        # Config Sliders
        sliders_row = ctk.CTkFrame(control_card, fg_color="transparent")
        sliders_row.pack(fill="x", padx=16, pady=(0, 14))

        # Files slider
        s1 = ctk.CTkFrame(sliders_row, fg_color="transparent")
        s1.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.lbl_fcount = ctk.CTkLabel(s1, text=f"Unorganized Misc Files: {self.num_files_var.get()}", font=Theme.get_font(11, "normal"), text_color=Theme.TEXT_MUTED)
        self.lbl_fcount.pack(anchor="w", pady=(0, 2))

        slider_f = ctk.CTkSlider(s1, from_=5, to=30, number_of_steps=25, variable=self.num_files_var, progress_color=Theme.ACCENT_CYAN, command=self._on_slider)
        slider_f.pack(fill="x")

        # Logs slider
        s2 = ctk.CTkFrame(sliders_row, fg_color="transparent")
        s2.pack(side="left", fill="x", expand=True, padx=4)

        self.lbl_lcount = ctk.CTkLabel(s2, text=f"Server Log Files: {self.num_logs_var.get()}", font=Theme.get_font(11, "normal"), text_color=Theme.TEXT_MUTED)
        self.lbl_lcount.pack(anchor="w", pady=(0, 2))

        slider_l = ctk.CTkSlider(s2, from_=1, to=10, number_of_steps=9, variable=self.num_logs_var, progress_color=Theme.ACCENT_PRIMARY, command=self._on_slider)
        slider_l.pack(fill="x")

        # Lines per log slider
        s3 = ctk.CTkFrame(sliders_row, fg_color="transparent")
        s3.pack(side="left", fill="x", expand=True, padx=(8, 0))

        self.lbl_lines = ctk.CTkLabel(s3, text=f"Lines Per Log File: {self.lines_per_log_var.get()}", font=Theme.get_font(11, "normal"), text_color=Theme.TEXT_MUTED)
        self.lbl_lines.pack(anchor="w", pady=(0, 2))

        slider_lines = ctk.CTkSlider(s3, from_=10, to=200, number_of_steps=19, variable=self.lines_per_log_var, progress_color=Theme.ACCENT_EMERALD, command=self._on_slider)
        slider_lines.pack(fill="x")

        # Action Buttons
        btn_row = ctk.CTkFrame(control_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(6, 16))

        gen_btn = ctk.CTkButton(
            btn_row,
            text="✨ Generate Mock Dataset",
            font=Theme.get_font(12, "bold"),
            height=38,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_HOVER,
            command=self._run_generate
        )
        gen_btn.pack(side="left", padx=(0, 10))

        self.test_suite_btn = ctk.CTkButton(
            btn_row,
            text="🚀 Run Full Test Suite Dump (UnitTests)",
            font=Theme.get_font(12, "bold"),
            height=38,
            fg_color=Theme.ACCENT_PURPLE,
            hover_color="#7C3AED",
            command=self._run_test_suite_dump
        )
        self.test_suite_btn.pack(side="left", padx=(0, 10))

        open_folder_btn = ctk.CTkButton(
            btn_row,
            text="📁 Open Folder",
            font=Theme.get_font(11, "bold"),
            height=38,
            fg_color=Theme.BG_CARD_HOVER,
            hover_color=Theme.ACCENT_PRIMARY,
            command=self._open_folder
        )
        open_folder_btn.pack(side="left")

        # Info Box
        info_card = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MEDIUM, border_width=1, border_color=Theme.BORDER_SUBTLE)
        info_card.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        info_lbl = ctk.CTkLabel(
            info_card,
            text="🧪 Instant Testing Lab:\n\n"
                 "• Creates a folder packed with unorganized documents (.pdf, .docx, .xlsx, .csv, .png, .jpg, .zip, .sql, .py, .exe).\n"
                 "• Generates realistic messy server logs (payment gateways, auth diagnostics, server errors).\n"
                 "• Injects hundreds of real emails, transaction IDs (TXN-XXXX, UUIDs, Stripe hashes), IPv4 addresses, and timestamps.\n"
                 "• 1-Click to immediately sort, parse, and verify all task requirements with real data!",
            font=Theme.get_font(12, "normal"),
            text_color=Theme.TEXT_MUTED,
            justify="left"
        )
        info_lbl.pack(anchor="w", padx=20, pady=20)

    def _browse_folder(self):
        f = filedialog.askdirectory(title="Select Mock Data Destination")
        if f:
            self.gen_dir_var.set(f)

    def _on_slider(self, *args):
        nf = self.num_files_var.get()
        nl = self.num_logs_var.get()
        lp = self.lines_per_log_var.get()
        self.lbl_fcount.configure(text=f"Unorganized Misc Files: {nf}")
        self.lbl_lcount.configure(text=f"Server Log Files: {nl}")
        self.lbl_lines.configure(text=f"Lines Per Log File: {lp}")
        self.card_sim_files.update_value(str(nf + nl), "Total files")
        self.card_sim_logs.update_value(str(nl * lp), "Simulated log entries")

    def _run_generate(self):
        target = self.gen_dir_var.get().strip()
        try:
            folder_created = generate_mock_environment(
                target_directory=target,
                num_files=self.num_files_var.get(),
                num_logs=self.num_logs_var.get(),
                lines_per_log=self.lines_per_log_var.get(),
                log_callback=self.log_terminal.log
            )
            show_toast(self, "Mock dataset generated successfully!", "success")
            if self.on_folder_generated:
                self.on_folder_generated(folder_created)
        except Exception as e:
            self.log_terminal.log("ERROR", f"Mock generator failed: {str(e)}")
            show_toast(self, f"Error: {str(e)}", "error")

    def _open_folder(self):
        target = self.gen_dir_var.get().strip()
        if not Path(target).exists():
            show_toast(self, "Folder does not exist yet. Click Generate first.", "warn")
            return
        os.startfile(target)

    def _run_test_suite_dump(self):
        """Runs the complete unittest suite and dumps real-time assertions and results into the terminal."""
        self.log_terminal.log("INFO", "🚀 [TEST SUITE] Executing full automated unit test suite (test_suite.py)...")
        self.test_suite_btn.configure(state="disabled")

        def worker():
            import test_suite
            suite = unittest.defaultTestLoader.loadTestsFromModule(test_suite)
            
            stream = io.StringIO()
            runner = unittest.TextTestRunner(stream=stream, verbosity=2)
            result = runner.run(suite)
            
            output = stream.getvalue()
            for line in output.strip().splitlines():
                if "ok" in line.lower() or "passed" in line.lower():
                    self.log_terminal.log("SUCCESS", f"   [PASS] {line}")
                elif "fail" in line.lower() or "error" in line.lower():
                    self.log_terminal.log("ERROR", f"   [FAIL] {line}")
                else:
                    self.log_terminal.log("INFO", f"   {line}")

            def finalize():
                self.test_suite_btn.configure(state="normal")
                if result.wasSuccessful():
                    self.card_status.update_value("PASSED", "All tests valid")
                    self.log_terminal.log("SUCCESS", f"🎉 [TEST SUITE COMPLETED] All {result.testsRun} automated tests PASSED flawlessly (0 errors, 0 failures)!")
                    show_toast(self, f"Test Suite Passed! {result.testsRun}/{result.testsRun} tests succeeded.", "success")
                else:
                    self.card_status.update_value("FAILED", f"{len(result.failures)} failures")
                    self.log_terminal.log("ERROR", f"❌ [TEST SUITE FAILED] {len(result.failures)} failures, {len(result.errors)} errors.")
                    show_toast(self, "Some unit tests failed. Check logs.", "error")

            self.after(0, finalize)

        threading.Thread(target=worker, daemon=True).start()

