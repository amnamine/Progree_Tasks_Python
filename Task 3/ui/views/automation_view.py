"""
Background Automation & Directory Watcher View Tab.
Manages the background daemon thread that continuously monitors folders,
auto-organizes files, and auto-parses new log streams into the master CSV.
"""

from tkinter import filedialog
import customtkinter as ctk
from pathlib import Path

from ui.theme import Theme
from ui.components.stat_card import StatCard
from ui.components.toast import show_toast
from core.watcher import AutomationWatcher
from core.file_organizer import FileOrganizer
from core.text_parser import TextParserEngine


class AutomationView(ctk.CTkFrame):
    def __init__(self, master, organizer: FileOrganizer, parser: TextParserEngine, log_terminal, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.organizer = organizer
        self.parser = parser
        self.log_terminal = log_terminal

        self.watch_dir_var = ctk.StringVar(value="")
        self.master_csv_var = ctk.StringVar(value=str(Path.cwd() / "daemon_master_logs.csv"))
        self.interval_var = ctk.IntVar(value=3)
        self.auto_sort_var = ctk.BooleanVar(value=True)
        self.auto_parse_var = ctk.BooleanVar(value=True)

        self.watcher = AutomationWatcher(
            target_dir="",
            master_csv_path=self.master_csv_var.get(),
            organizer=self.organizer,
            parser=self.parser,
            poll_interval_sec=self.interval_var.get()
        )
        self.watcher.on_log = self.log_terminal.log
        self.watcher.on_status_change = self._on_status_change
        self.watcher.on_cycle_completed = self._on_cycle_completed

        self._build_ui()

    def _build_ui(self):
        # Top Metrics
        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(fill="x", padx=16, pady=(12, 8))

        self.card_daemon_status = StatCard(stats_row, "Daemon Engine", "STOPPED", "⚙️", Theme.TEXT_MUTED, "Standing by")
        self.card_daemon_status.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.card_auto_sorted = StatCard(stats_row, "Auto-Sorted Files", "0", "📥", Theme.ACCENT_EMERALD, "Auto-classified")
        self.card_auto_sorted.pack(side="left", fill="x", expand=True, padx=4)

        self.card_auto_entities = StatCard(stats_row, "Logged to Master CSV", "0", "📊", Theme.ACCENT_CYAN, "Entities parsed")
        self.card_auto_entities.pack(side="left", fill="x", expand=True, padx=(8, 0))

        # Main Control Card
        control_card = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MEDIUM, border_width=1, border_color=Theme.BORDER_SUBTLE)
        control_card.pack(fill="x", padx=16, pady=8)

        # Monitored Folder Picker Row
        mon_row = ctk.CTkFrame(control_card, fg_color="transparent")
        mon_row.pack(fill="x", padx=16, pady=(14, 10))

        lbl_mon = ctk.CTkLabel(mon_row, text="Folder to Continuously Monitor:", font=Theme.get_font(12, "bold"), text_color=Theme.TEXT_MAIN)
        lbl_mon.pack(anchor="w", pady=(0, 4))

        picker_box = ctk.CTkFrame(mon_row, fg_color="transparent")
        picker_box.pack(fill="x")

        self.mon_entry = ctk.CTkEntry(
            picker_box,
            textvariable=self.watch_dir_var,
            placeholder_text="Select directory to watch in background...",
            font=Theme.get_font(12, "normal"),
            height=36,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER_SUBTLE
        )
        self.mon_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        browse_btn = ctk.CTkButton(
            picker_box,
            text="📁 Select Folder",
            font=Theme.get_font(11, "bold"),
            width=110,
            height=36,
            fg_color=Theme.ACCENT_PRIMARY,
            hover_color=Theme.ACCENT_HOVER,
            command=self._browse_folder
        )
        browse_btn.pack(side="left")

        # Master CSV output row
        csv_row = ctk.CTkFrame(control_card, fg_color="transparent")
        csv_row.pack(fill="x", padx=16, pady=(0, 10))

        lbl_csv = ctk.CTkLabel(csv_row, text="Target Master CSV Destination:", font=Theme.get_font(11, "bold"), text_color=Theme.TEXT_MUTED)
        lbl_csv.pack(anchor="w", pady=(0, 4))

        csv_picker_box = ctk.CTkFrame(csv_row, fg_color="transparent")
        csv_picker_box.pack(fill="x")

        self.csv_entry = ctk.CTkEntry(
            csv_picker_box,
            textvariable=self.master_csv_var,
            font=Theme.get_font(11, "normal"),
            height=32,
            fg_color=Theme.BG_INPUT,
            border_color=Theme.BORDER_SUBTLE
        )
        self.csv_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        csv_browse_btn = ctk.CTkButton(
            csv_picker_box,
            text="Change CSV...",
            font=Theme.get_font(10, "bold"),
            width=90,
            height=32,
            fg_color=Theme.BG_CARD_HOVER,
            hover_color=Theme.ACCENT_PRIMARY,
            command=self._browse_csv
        )
        csv_browse_btn.pack(side="left")

        # Daemon Configuration & Automation Switches
        switches_row = ctk.CTkFrame(control_card, fg_color="transparent")
        switches_row.pack(fill="x", padx=16, pady=(0, 12))

        self.switch_sort = ctk.CTkSwitch(
            switches_row,
            text="Auto-Sort Incoming Files by Extension",
            variable=self.auto_sort_var,
            font=Theme.get_font(11, "normal"),
            progress_color=Theme.ACCENT_EMERALD,
            command=self._update_switches
        )
        self.switch_sort.pack(side="left", padx=(0, 20))

        self.switch_parse = ctk.CTkSwitch(
            switches_row,
            text="Auto-Parse New Logs & Stream to Master CSV",
            variable=self.auto_parse_var,
            font=Theme.get_font(11, "normal"),
            progress_color=Theme.ACCENT_CYAN,
            command=self._update_switches
        )
        self.switch_parse.pack(side="left")

        # Interval Slider
        interval_row = ctk.CTkFrame(control_card, fg_color="transparent")
        interval_row.pack(fill="x", padx=16, pady=(0, 14))

        self.lbl_interval = ctk.CTkLabel(
            interval_row,
            text=f"Poll Frequency Interval: {self.interval_var.get()}s",
            font=Theme.get_font(11, "normal"),
            text_color=Theme.TEXT_MUTED
        )
        self.lbl_interval.pack(anchor="w", pady=(0, 4))

        self.slider = ctk.CTkSlider(
            interval_row,
            from_=1,
            to=30,
            number_of_steps=29,
            variable=self.interval_var,
            progress_color=Theme.ACCENT_PRIMARY,
            button_color=Theme.ACCENT_CYAN,
            command=self._on_slider_change
        )
        self.slider.pack(fill="x")

        # Master Controls (Start / Pause / Stop)
        btn_row = ctk.CTkFrame(control_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=16, pady=(4, 14))

        self.start_btn = ctk.CTkButton(
            btn_row,
            text="▶ Start Background Daemon",
            font=Theme.get_font(12, "bold"),
            height=38,
            fg_color=Theme.ACCENT_EMERALD,
            hover_color="#059669",
            command=self._start_daemon
        )
        self.start_btn.pack(side="left", padx=(0, 8))

        self.pause_btn = ctk.CTkButton(
            btn_row,
            text="⏸ Pause",
            font=Theme.get_font(12, "bold"),
            height=38,
            fg_color=Theme.BG_CARD_HOVER,
            hover_color=Theme.ACCENT_AMBER,
            state="disabled",
            command=self._toggle_pause
        )
        self.pause_btn.pack(side="left", padx=8)

        self.stop_btn = ctk.CTkButton(
            btn_row,
            text="⏹ Stop Daemon",
            font=Theme.get_font(12, "bold"),
            height=38,
            fg_color=Theme.BG_CARD_HOVER,
            hover_color=Theme.ACCENT_ROSE,
            state="disabled",
            command=self._stop_daemon
        )
        self.stop_btn.pack(side="left", padx=8)

        # Info Card
        info_card = ctk.CTkFrame(self, fg_color=Theme.BG_CARD, corner_radius=Theme.RADIUS_MEDIUM, border_width=1, border_color=Theme.BORDER_SUBTLE)
        info_card.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        info_lbl = ctk.CTkLabel(
            info_card,
            text="⚡ Background Automation Daemon Operating Principle:\n\n"
                 "• Any new flat log or file placed in the monitored directory is automatically detected in real-time.\n"
                 "• Log files are parsed for email patterns, transaction IDs, IPs, and errors, and appended cleanly to Master CSV.\n"
                 "• Files are instantly organized into categorized subdirectories (Documents, Images, Spreadsheets, Logs, etc.).\n"
                 "• Runs entirely in a background thread without freezing the user interface.",
            font=Theme.get_font(12, "normal"),
            text_color=Theme.TEXT_MUTED,
            justify="left"
        )
        info_lbl.pack(anchor="w", padx=20, pady=20)

    def _browse_folder(self):
        folder = filedialog.askdirectory(title="Select Folder for Background Monitoring")
        if folder:
            self.watch_dir_var.set(folder)

    def _browse_csv(self):
        file = filedialog.asksaveasfilename(
            title="Select Target Master CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )
        if file:
            self.master_csv_var.set(file)

    def set_target_directory(self, path_str: str):
        self.watch_dir_var.set(path_str)

    def _on_slider_change(self, val):
        sec = int(val)
        self.lbl_interval.configure(text=f"Poll Frequency Interval: {sec}s")
        self.watcher.poll_interval = sec

    def _update_switches(self):
        self.watcher.auto_organize = self.auto_sort_var.get()
        self.watcher.auto_parse_logs = self.auto_parse_var.get()

    def _start_daemon(self):
        target = self.watch_dir_var.get().strip()
        if not target or not Path(target).is_dir():
            show_toast(self, "Please select a valid directory to monitor.", "warn")
            return

        self.watcher.target_dir = target
        self.watcher.master_csv_path = self.master_csv_var.get().strip()
        self.watcher.poll_interval = self.interval_var.get()
        self.watcher.auto_organize = self.auto_sort_var.get()
        self.watcher.auto_parse_logs = self.auto_parse_var.get()

        self.watcher.start()
        self.start_btn.configure(state="disabled")
        self.pause_btn.configure(state="normal", text="⏸ Pause")
        self.stop_btn.configure(state="normal")
        show_toast(self, "Background Daemon is now ACTIVE and monitoring!", "success")

    def _toggle_pause(self):
        if self.watcher.is_paused:
            self.watcher.resume()
            self.pause_btn.configure(text="⏸ Pause")
            show_toast(self, "Daemon resumed.", "info")
        else:
            self.watcher.pause()
            self.pause_btn.configure(text="▶ Resume")
            show_toast(self, "Daemon paused.", "warn")

    def _stop_daemon(self):
        self.watcher.stop()
        self.start_btn.configure(state="normal")
        self.pause_btn.configure(state="disabled")
        self.stop_btn.configure(state="disabled")
        show_toast(self, "Daemon stopped.", "info")

    def _on_status_change(self, status: str):
        color = Theme.ACCENT_EMERALD if status == "RUNNING" else (Theme.ACCENT_AMBER if status == "PAUSED" else Theme.TEXT_MUTED)
        self.card_daemon_status.update_value(status, f"Watcher: {status.lower()}")
        self.card_daemon_status.stripe.configure(fg_color=color)

    def _on_cycle_completed(self, stats: dict):
        self.after(0, lambda: self.card_auto_sorted.update_value(str(stats["files_organized"]), f"Cycles: {stats['total_cycles']}"))
        self.after(0, lambda: self.card_auto_entities.update_value(str(stats["entities_extracted"]), f"Last: {stats.get('last_activity', 'N/A')}"))
