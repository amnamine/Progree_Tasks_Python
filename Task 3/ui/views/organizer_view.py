"""
File Organizer View Tab.
Allows selecting an unorganized directory, configuring sorting rules,
previewing dry-run moves in a table, executing file sorting, and undoing operations.
"""

import os
import threading
from tkinter import filedialog, ttk
import customtkinter as ctk
from pathlib import Path

from ui.theme import Theme
from ui.components.stat_card import StatCard
from ui.components.toast import show_toast
from core.file_organizer import FileOrganizer, DEFAULT_CATEGORIES
from core.mock_generator import generate_mock_environment


class OrganizerView(ctk.CTkFrame):
    def __init__(self, master, organizer: FileOrganizer, log_terminal, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.organizer = organizer
        self.log_terminal = log_terminal
        self.selected_dir = ctk.StringVar(value="")
        self.collision_mode = ctk.StringVar(value="rename")
        self.recursive_var = ctk.BooleanVar(value=False)
        self.category_vars = {}

        self._build_ui()

    def _build_ui(self):
        # Top Stat Row
        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(fill="x", padx=16, pady=(12, 8))

        self.card_total = StatCard(stats_row, "Scanned Files", "0", "📁", Theme.ACCENT_PRIMARY, "Ready to analyze")
        self.card_total.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.card_organized = StatCard(stats_row, "Organized Batches", str(len(self.organizer.undo_history)), "🗂️", Theme.ACCENT_EMERALD, "Recorded in history")
        self.card_organized.pack(side="left", fill="x", expand=True, padx=4)

        self.card_categories = StatCard(stats_row, "Categories Configured", str(len(self.organizer.categories)), "🏷️", Theme.ACCENT_PURPLE, "Default rule set")
        self.card_categories.pack(side="left", fill="x", expand=True, padx=(8, 0))

        # Main Control Card
        control_card = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MEDIUM, border_width=1, border_color=Theme.BORDER_SUBTLE)
        control_card.pack(fill="x", padx=16, pady=8)

        # Folder Selection Row
        dir_frame = ctk.CTkFrame(control_card, fg_color="transparent")
        dir_frame.pack(fill="x", padx=16, pady=(14, 10))

        lbl = ctk.CTkLabel(dir_frame, text="Target Unorganized Folder:", font=Theme.get_font(12, "bold"), text_color=Theme.TEXT_MAIN)
        lbl.pack(anchor="w", pady=(0, 4))

        picker_box = ctk.CTkFrame(dir_frame, fg_color="transparent")
        picker_box.pack(fill="x")

        self.dir_entry = ctk.CTkEntry(
            picker_box,
            textvariable=self.selected_dir,
            placeholder_text="Select or type the directory containing unorganized files...",
            font=Theme.get_font(12, "normal"),
            height=36,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER_SUBTLE
        )
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_btn = ctk.CTkButton(
            picker_box,
            text="📁 Browse...",
            font=Theme.get_font(12, "bold"),
            width=110,
            height=36,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_HOVER,
            command=self._browse_folder
        )
        browse_btn.pack(side="left")

        # Configuration Row (Recursive, Collision Mode, Categories)
        config_row = ctk.CTkFrame(control_card, fg_color="transparent")
        config_row.pack(fill="x", padx=16, pady=(0, 12))

        # Collision Mode Dropdown
        collision_box = ctk.CTkFrame(config_row, fg_color="transparent")
        collision_box.pack(side="left", padx=(0, 16))

        c_lbl = ctk.CTkLabel(collision_box, text="Duplicate Resolution:", font=Theme.get_font(11, "normal"), text_color=Theme.TEXT_MUTED)
        c_lbl.pack(anchor="w")

        self.collision_dropdown = ctk.CTkOptionMenu(
            collision_box,
            values=["Auto-Rename (_1, _2)", "Overwrite", "Skip"],
            font=Theme.get_font(11, "normal"),
            height=30,
            fg_color=Theme.BG_CARD_HOVER,
            button_color=Theme.ACCENT_PRIMARY,
            command=self._on_collision_change
        )
        self.collision_dropdown.set("Auto-Rename (_1, _2)")
        self.collision_dropdown.pack(anchor="w", pady=(2, 0))

        # Recursive switch
        self.rec_switch = ctk.CTkSwitch(
            config_row,
            text="Include Subdirectories (Recursive)",
            variable=self.recursive_var,
            font=Theme.get_font(11, "normal"),
            progress_color=Theme.ACCENT_PRIMARY
        )
        self.rec_switch.pack(side="left", padx=(16, 0), pady=(16, 0))

        # Action Buttons Row
        action_row = ctk.CTkFrame(control_card, fg_color="transparent")
        action_row.pack(fill="x", padx=16, pady=(4, 14))

        self.preview_btn = ctk.CTkButton(
            action_row,
            text="🔍 Dry Run Preview",
            font=Theme.get_font(12, "bold"),
            height=38,
            fg_color=Theme.ACCENT_CYAN,
            text_color="#0F172A",
            hover_color="#0891B2",
            command=self._run_preview
        )
        self.preview_btn.pack(side="left", padx=(0, 8))

        self.organize_btn = ctk.CTkButton(
            action_row,
            text="⚡ Sort & Organize Files",
            font=Theme.get_font(12, "bold"),
            height=38,
            fg_color=Theme.ACCENT_EMERALD,
            hover_color="#059669",
            command=self._run_organize
        )
        self.organize_btn.pack(side="left", padx=8)

        self.undo_btn = ctk.CTkButton(
            action_row,
            text="↩ Undo Last Sort",
            font=Theme.get_font(12, "bold"),
            height=38,
            fg_color=Theme.BG_CARD_HOVER,
            hover_color=Theme.ACCENT_ROSE,
            command=self._run_undo
        )
        self.undo_btn.pack(side="left", padx=8)

        self.test_dump_btn = ctk.CTkButton(
            action_row,
            text="🧪 Quick Auto-Test Dump",
            font=Theme.get_font(12, "bold"),
            height=38,
            fg_color=Theme.ACCENT_PURPLE,
            hover_color="#7C3AED",
            command=self._run_quick_test_dump
        )
        self.test_dump_btn.pack(side="right", padx=(8, 0))

        # Progress Bar & Status Text
        self.progress_bar = ctk.CTkProgressBar(
            self,
            height=6,
            corner_radius=3,
            progress_color=Theme.ACCENT_PRIMARY,
            fg_color=Theme.BG_CARD
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=16, pady=(4, 6))

        self.status_label = ctk.CTkLabel(
            self,
            text="Select a directory to begin file organization.",
            font=Theme.get_font(11, "normal"),
            text_color=Theme.TEXT_MUTED
        )
        self.status_label.pack(anchor="w", padx=18, pady=(0, 6))

        # Preview Table Frame
        table_container = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MEDIUM, border_width=1, border_color=Theme.BORDER_SUBTLE)
        table_container.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        # Table Header
        tbl_header = ctk.CTkFrame(table_container, fg_color="transparent", height=32)
        tbl_header.pack(fill="x", padx=12, pady=(10, 4))

        lbl_tbl = ctk.CTkLabel(tbl_header, text="File Organization Plan / Preview", font=Theme.get_font(12, "bold"), text_color=Theme.TEXT_MAIN)
        lbl_tbl.pack(side="left")

        self.tbl_count = ctk.CTkLabel(tbl_header, text="0 items listed", font=Theme.get_font(11, "normal"), text_color=Theme.TEXT_DIM)
        self.tbl_count.pack(side="right")

        # Treeview styled for modern dark mode
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Organizer.Treeview",
            background=Theme.BG_LOG,
            foreground=Theme.TEXT_MAIN,
            fieldbackground=Theme.BG_LOG,
            rowheight=26,
            font=Theme.get_font(10, "normal")
        )
        style.configure(
            "Organizer.Treeview.Heading",
            background=Theme.BG_CARD_HOVER,
            foreground=Theme.TEXT_MAIN,
            font=Theme.get_font(10, "bold"),
            relief="flat"
        )
        style.map("Organizer.Treeview", background=[("selected", Theme.ACCENT_PRIMARY)])

        tree_scroll_y = ctk.CTkScrollbar(table_container)
        tree_scroll_y.pack(side="right", fill="y", padx=(0, 4), pady=(0, 10))

        self.tree = ttk.Treeview(
            table_container,
            columns=("file", "category", "target", "size"),
            show="headings",
            style="Organizer.Treeview",
            yscrollcommand=tree_scroll_y.set
        )
        tree_scroll_y.configure(command=self.tree.yview)

        self.tree.heading("file", text="Source File")
        self.tree.heading("category", text="Category")
        self.tree.heading("target", text="Target Destination Path")
        self.tree.heading("size", text="Size")

        self.tree.column("file", width=220, anchor="w")
        self.tree.column("category", width=140, anchor="center")
        self.tree.column("target", width=420, anchor="w")
        self.tree.column("size", width=90, anchor="e")

        self.tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Select Directory to Organize")
        if folder:
            self.selected_dir.set(folder)
            self._run_preview()

    def set_target_directory(self, path_str: str):
        self.selected_dir.set(path_str)
        self._run_preview()

    def _on_collision_change(self, choice: str):
        if "Rename" in choice:
            self.collision_mode.set("rename")
        elif "Overwrite" in choice:
            self.collision_mode.set("overwrite")
        else:
            self.collision_mode.set("skip")

    def _run_preview(self):
        target = self.selected_dir.get().strip()
        if not target or not Path(target).is_dir():
            show_toast(self, "Please select a valid directory first.", "warn")
            return

        self.tree.delete(*self.tree.get_children())
        try:
            preview_items = self.organizer.preview_organize(target, recursive=self.recursive_var.get())
            self.card_total.update_value(str(len(preview_items)), "Files to sort")
            self.tbl_count.configure(text=f"{len(preview_items)} files scheduled")

            for fname, orig_path, dest_path, size in preview_items:
                cat = self.organizer.get_category_for_file(fname)
                size_str = f"{size / 1024:.1f} KB" if size >= 1024 else f"{size} B"
                self.tree.insert("", "end", values=(fname, cat, dest_path, size_str))

            self.status_label.configure(text=f"Dry run complete: {len(preview_items)} files ready for sorting.")
            self.log_terminal.log("INFO", f"Dry run preview for '{target}': {len(preview_items)} candidate files found.")
            show_toast(self, f"Found {len(preview_items)} files to organize.", "info")
        except Exception as e:
            self.log_terminal.log("ERROR", f"Preview failed: {str(e)}")
            show_toast(self, f"Error: {str(e)}", "error")

    def _run_organize(self):
        target = self.selected_dir.get().strip()
        if not target or not Path(target).is_dir():
            show_toast(self, "Please select a valid directory first.", "warn")
            return

        self.preview_btn.configure(state="disabled")
        self.organize_btn.configure(state="disabled")
        self.undo_btn.configure(state="disabled")

        def worker():
            def progress(current, total, msg):
                frac = current / total if total > 0 else 0
                self.after(0, lambda: self.progress_bar.set(frac))
                self.after(0, lambda: self.status_label.configure(text=f"[{current}/{total}] {msg}"))

            successful, errors, records = self.organizer.organize(
                target_dir=target,
                recursive=self.recursive_var.get(),
                collision_mode=self.collision_mode.get(),
                progress_callback=progress,
                log_callback=self.log_terminal.log
            )

            def finalize():
                self.preview_btn.configure(state="normal")
                self.organize_btn.configure(state="normal")
                self.undo_btn.configure(state="normal")
                self.card_organized.update_value(str(len(self.organizer.undo_history)), "Recorded in history")
                self.progress_bar.set(1.0)
                self.status_label.configure(text=f"Completed: {successful} files moved to category folders ({errors} errors).")
                self._run_preview()
                show_toast(self, f"Successfully organized {successful} files!", "success")

            self.after(0, finalize)

        threading.Thread(target=worker, daemon=True).start()

    def _run_undo(self):
        restored, errors = self.organizer.undo_last(log_callback=self.log_terminal.log)
        self.card_organized.update_value(str(len(self.organizer.undo_history)), "Recorded in history")
        self._run_preview()
        if restored > 0:
            show_toast(self, f"Undid last sort: {restored} files restored.", "success")
        else:
            show_toast(self, "Nothing to undo.", "warn")

    def _run_quick_test_dump(self):
        """Automated 1-Click Test: Generates mock messy files, previews dry-run, and sorts automatically."""
        self.log_terminal.log("INFO", "🚀 [AUTO-TEST] Starting automated File Organizer test dump...")
        self.test_dump_btn.configure(state="disabled")

        def worker():
            test_dir = Path.cwd() / "sample_unorganized_data"
            test_dir.mkdir(parents=True, exist_ok=True)

            # 1. Generate test files
            self.log_terminal.log("INFO", f"1. Populating '{test_dir.name}' with fresh unorganized mock files...")
            generate_mock_environment(
                str(test_dir),
                num_files=10,
                num_logs=3,
                lines_per_log=20,
                log_callback=self.log_terminal.log
            )

            self.after(0, lambda: self.selected_dir.set(str(test_dir.resolve())))
            self.after(0, self._run_preview)

            # 2. Wait 0.6s to allow UI preview rendering, then run auto sort
            import time
            time.sleep(0.6)

            self.log_terminal.log("INFO", "2. Executing automated categorization and file organization...")
            successful, errors, records = self.organizer.organize(
                target_dir=str(test_dir),
                recursive=self.recursive_var.get(),
                collision_mode="rename",
                log_callback=self.log_terminal.log
            )

            def finalize():
                self.test_dump_btn.configure(state="normal")
                self.card_organized.update_value(str(len(self.organizer.undo_history)), "Recorded in history")
                self.progress_bar.set(1.0)
                self.status_label.configure(text=f"Auto-Test Passed: {successful} files classified into categories ({errors} errors).")
                self._run_preview()
                self.log_terminal.log("SUCCESS", f"✅ [AUTO-TEST COMPLETE] File Organizer sorted {successful} files into category folders!")
                show_toast(self, f"Auto-Test Done! {successful} files organized automatically.", "success")

            self.after(0, finalize)

        threading.Thread(target=worker, daemon=True).start()

