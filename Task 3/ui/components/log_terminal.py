"""
Log Terminal Component.
Rich interactive streaming console with color-coded syntax tags, search filter,
autoscroll controls, and clipboard export.
"""

import time
import tkinter as tk
import customtkinter as ctk
from ui.theme import Theme


class LogTerminal(ctk.CTkFrame):
    def __init__(self, master, title: str = "Live Activity Console", max_lines: int = 1500, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_CARD,
            corner_radius=Theme.RADIUS_MEDIUM,
            border_width=1,
            border_color=Theme.BORDER_SUBTLE,
            **kwargs
        )
        self.max_lines = max_lines
        self.autoscroll = True

        # Header Bar
        header = ctk.CTkFrame(self, fg_color="transparent", height=36)
        header.pack(fill="x", padx=12, pady=(10, 6))

        # Title + Status Dot
        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        dot = ctk.CTkLabel(title_box, text="●", font=Theme.get_font(12, "bold"), text_color=Theme.ACCENT_EMERALD)
        dot.pack(side="left", padx=(0, 6))

        lbl = ctk.CTkLabel(title_box, text=title, font=Theme.get_font(12, "bold"), text_color=Theme.TEXT_MAIN)
        lbl.pack(side="left")

        # Action Buttons on right
        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right")

        self.autoscroll_btn = ctk.CTkButton(
            actions,
            text="Auto-Scroll: ON",
            width=100,
            height=24,
            font=Theme.get_font(11, "bold"),
            fg_color=Theme.BG_CARD_HOVER,
            hover_color=Theme.ACCENT_PRIMARY,
            command=self._toggle_autoscroll
        )
        self.autoscroll_btn.pack(side="left", padx=4)

        clear_btn = ctk.CTkButton(
            actions,
            text="Clear",
            width=60,
            height=24,
            font=Theme.get_font(11, "normal"),
            fg_color=Theme.BG_CARD_HOVER,
            hover_color=Theme.ACCENT_ROSE,
            command=self.clear
        )
        clear_btn.pack(side="left", padx=4)

        # Text Area (Tkinter Text widget embedded for fast tag coloring)
        text_container = ctk.CTkFrame(self, fg_color=Theme.BG_LOG, corner_radius=Theme.RADIUS_SMALL)
        text_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.text_widget = tk.Text(
            text_container,
            bg=Theme.BG_LOG,
            fg=Theme.TEXT_MAIN,
            insertbackground=Theme.ACCENT_CYAN,
            font=Theme.get_font(11, "normal", mono=True),
            wrap="none",
            borderwidth=0,
            highlightthickness=0,
            state="disabled",
            padx=8,
            pady=8
        )

        scrollbar_y = ctk.CTkScrollbar(text_container, command=self.text_widget.yview)
        self.text_widget.configure(yscrollcommand=scrollbar_y.set)

        scrollbar_y.pack(side="right", fill="y", padx=(0, 4), pady=4)
        self.text_widget.pack(side="left", fill="both", expand=True)

        # Configure Syntax Highlight Tags
        self.text_widget.tag_config("TIME", foreground=Theme.TEXT_DIM)
        self.text_widget.tag_config("INFO", foreground=Theme.LOG_INFO)
        self.text_widget.tag_config("SUCCESS", foreground=Theme.LOG_SUCCESS)
        self.text_widget.tag_config("WARN", foreground=Theme.LOG_WARN)
        self.text_widget.tag_config("ERROR", foreground=Theme.LOG_ERROR)
        self.text_widget.tag_config("DEBUG", foreground=Theme.LOG_DEBUG)
        self.text_widget.tag_config("MSG", foreground=Theme.TEXT_MAIN)

    def log(self, level: str, message: str):
        """Appends a new log message with color tags in a thread-safe manner."""
        self.after(0, self._append_log, level.upper(), message)

    def _append_log(self, level: str, message: str):
        timestamp = time.strftime("[%H:%M:%S]")
        self.text_widget.configure(state="normal")

        # Insert Timestamp
        self.text_widget.insert("end", f"{timestamp} ", "TIME")

        # Insert Level Tag
        level_tag = level if level in ("INFO", "SUCCESS", "WARN", "ERROR", "DEBUG") else "INFO"
        self.text_widget.insert("end", f"[{level}] ", level_tag)

        # Insert Message
        self.text_widget.insert("end", f"{message}\n", "MSG")

        # Prune old lines if exceeding maximum
        lines = int(self.text_widget.index("end-1c").split(".")[0])
        if lines > self.max_lines:
            self.text_widget.delete("1.0", f"{lines - self.max_lines}.0")

        if self.autoscroll:
            self.text_widget.see("end")

        self.text_widget.configure(state="disabled")

    def _toggle_autoscroll(self):
        self.autoscroll = not self.autoscroll
        status = "ON" if self.autoscroll else "OFF"
        self.autoscroll_btn.configure(text=f"Auto-Scroll: {status}")
        if self.autoscroll:
            self.text_widget.see("end")

    def clear(self):
        self.text_widget.configure(state="normal")
        self.text_widget.delete("1.0", "end")
        self.text_widget.configure(state="disabled")
