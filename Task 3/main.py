"""
Main Desktop Application Entrypoint.
Automated File Operating & Text-Parsing Desktop Suite.
"""

import sys
import tkinter as tk
import customtkinter as ctk
from pathlib import Path

from core.file_organizer import FileOrganizer
from core.text_parser import TextParserEngine
from ui.theme import Theme
from ui.components.log_terminal import LogTerminal
from ui.views.organizer_view import OrganizerView
from ui.views.parser_view import ParserView
from ui.views.automation_view import AutomationView
from ui.views.master_csv_view import MasterCsvView
from ui.views.generator_view import GeneratorView


class AutoFileParserApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Appearance & Window Configuration
        ctk.set_appearance_mode(Theme.APPEARANCE_MODE)
        ctk.set_default_color_theme(Theme.COLOR_THEME)

        self.title("AutoFile & LogParser Pro • Automation Suite")
        self.geometry("1240x820")
        self.minsize(1050, 720)
        self.configure(fg_color=Theme.BG_DARK)

        # Core Engines
        self.organizer = FileOrganizer()
        self.parser = TextParserEngine()

        # Layout Setup
        self._build_layout()
        self._select_tab("organizer")

        # Initial Welcome Log
        self.log_terminal.log("INFO", "AutoFile & LogParser Pro Suite initialized.")
        self.log_terminal.log("INFO", "Standard system libraries: os, shutil, re, pathlib, csv, threading.")
        self.log_terminal.log("SUCCESS", "System ready. Use 'Test Generator' tab for instant 1-click sample datasets.")

    def _build_layout(self):
        # Master Horizontal Split (Sidebar | Main Content Area)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # 1. Left Navigation Sidebar
        self.sidebar = ctk.CTkFrame(
            self,
            width=240,
            corner_radius=0,
            fg_color=Theme.BG_SIDEBAR,
            border_width=1,
            border_color=Theme.BORDER_SUBTLE
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1)

        # App Brand / Logo Header
        brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        brand_frame.pack(fill="x", padx=16, pady=(20, 16))

        title_lbl = ctk.CTkLabel(
            brand_frame,
            text="⚡ AutoFile Pro",
            font=Theme.get_font(18, "bold"),
            text_color=Theme.TEXT_MAIN,
            anchor="w"
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = ctk.CTkLabel(
            brand_frame,
            text="File Ops & Regex Log Parser",
            font=Theme.get_font(11, "normal"),
            text_color=Theme.TEXT_ACCENT,
            anchor="w"
        )
        subtitle_lbl.pack(anchor="w", pady=(2, 0))

        # Nav Buttons Container
        self.nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_frame.pack(fill="x", padx=10, pady=6)

        self.nav_buttons = {}
        nav_items = [
            ("organizer", "🗂️  File Organizer", "Manage & sort local folders"),
            ("parser", "⚡  Regex Log Parser", "Extract emails, TXNs & IPs"),
            ("automation", "⚙️  Background Daemon", "Continuous folder monitor"),
            ("master_csv", "📑  Master CSV Explorer", "Clean structured data log"),
            ("generator", "🧪  Test Data Lab", "1-Click mock data maker"),
        ]

        for tab_id, label, desc in nav_items:
            btn = ctk.CTkButton(
                self.nav_frame,
                text=label,
                font=Theme.get_font(13, "bold"),
                height=42,
                corner_radius=Theme.RADIUS_SMALL,
                anchor="w",
                fg_color="transparent",
                text_color=Theme.TEXT_MAIN,
                hover_color=Theme.BG_CARD_HOVER,
                command=lambda tid=tab_id: self._select_tab(tid)
            )
            btn.pack(fill="x", pady=4)
            self.nav_buttons[tab_id] = btn

        # Sidebar Footer: Theme Toggle & Info
        sidebar_footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_footer.pack(side="bottom", fill="x", padx=16, pady=16)

        theme_lbl = ctk.CTkLabel(
            sidebar_footer,
            text="Appearance Mode",
            font=Theme.get_font(11, "normal"),
            text_color=Theme.TEXT_DIM,
            anchor="w"
        )
        theme_lbl.pack(anchor="w", pady=(0, 4))

        self.theme_menu = ctk.CTkOptionMenu(
            sidebar_footer,
            values=["Dark", "Light", "System"],
            font=Theme.get_font(11, "normal"),
            height=28,
            fg_color=Theme.BG_CARD,
            button_color=Theme.ACCENT_PRIMARY,
            command=self._change_appearance_mode
        )
        self.theme_menu.set("Dark")
        self.theme_menu.pack(fill="x", pady=(0, 10))

        credit_lbl = ctk.CTkLabel(
            sidebar_footer,
            text="Python Internship • Task 3",
            font=Theme.get_font(10, "normal"),
            text_color=Theme.TEXT_DIM,
            anchor="center"
        )
        credit_lbl.pack()

        # 2. Right Workspace Area (Views + Terminal)
        self.right_workspace = ctk.CTkFrame(self, fg_color="transparent")
        self.right_workspace.grid(row=0, column=1, sticky="nsew")
        self.right_workspace.grid_rowconfigure(0, weight=3) # Views area
        self.right_workspace.grid_rowconfigure(1, weight=1) # Log terminal area
        self.right_workspace.grid_columnconfigure(0, weight=1)

        # View Tabs Container
        self.views_container = ctk.CTkFrame(self.right_workspace, fg_color="transparent")
        self.views_container.grid(row=0, column=0, sticky="nsew")
        self.views_container.grid_rowconfigure(0, weight=1)
        self.views_container.grid_columnconfigure(0, weight=1)

        # Bottom Live Terminal
        self.log_terminal = LogTerminal(self.right_workspace, height=180)
        self.log_terminal.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 14))

        # Instantiate View Tabs
        self.views = {
            "organizer": OrganizerView(self.views_container, self.organizer, self.log_terminal),
            "parser": ParserView(self.views_container, self.parser, self.log_terminal, on_export_callback=self._on_csv_exported),
            "automation": AutomationView(self.views_container, self.organizer, self.parser, self.log_terminal),
            "master_csv": MasterCsvView(self.views_container, self.log_terminal),
            "generator": GeneratorView(self.views_container, self.log_terminal, on_folder_generated=self._on_folder_generated)
        }

        for view in self.views.values():
            view.grid(row=0, column=0, sticky="nsew")

    def _select_tab(self, tab_id: str):
        # Update sidebar button highlight states
        for tid, btn in self.nav_buttons.items():
            if tid == tab_id:
                btn.configure(
                    fg_color=Theme.ACCENT_PRIMARY,
                    text_color="#FFFFFF"
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=Theme.TEXT_MAIN
                )

        # Raise selected view
        target_view = self.views.get(tab_id)
        if target_view:
            target_view.tkraise()

    def _on_folder_generated(self, folder_path: str):
        """Cross-tab handler: when test data is generated, update paths in other views."""
        self.views["organizer"].set_target_directory(folder_path)
        self.views["parser"].set_target_path(folder_path)
        self.views["automation"].set_target_directory(folder_path)
        self._select_tab("organizer")

    def _on_csv_exported(self, csv_path: str):
        """Cross-tab handler: when CSV is exported, reload in Master CSV view."""
        self.views["master_csv"].set_csv_path(csv_path)

    def _change_appearance_mode(self, new_mode: str):
        ctk.set_appearance_mode(new_mode)


def main():
    app = AutoFileParserApp()
    app.mainloop()


if __name__ == "__main__":
    main()
