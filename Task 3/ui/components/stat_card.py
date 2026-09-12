"""
Metric Stat Card Component.
Displays animated count, title, icon, and colorful glow accent.
"""

import customtkinter as ctk
from ui.theme import Theme


class StatCard(ctk.CTkFrame):
    def __init__(
        self,
        master,
        title: str,
        value: str = "0",
        icon: str = "📊",
        accent_color: str = Theme.ACCENT_PRIMARY,
        subtitle: str = "",
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=Theme.BG_CARD,
            corner_radius=Theme.RADIUS_MEDIUM,
            border_width=1,
            border_color=Theme.BORDER_SUBTLE,
            **kwargs
        )
        self.accent_color = accent_color

        # Top Accent stripe indicator
        self.stripe = ctk.CTkFrame(
            self,
            fg_color=self.accent_color,
            height=3,
            corner_radius=0
        )
        self.stripe.pack(fill="x", side="top")

        # Container
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=12)

        # Header Row (Title + Icon)
        header_row = ctk.CTkFrame(content, fg_color="transparent")
        header_row.pack(fill="x")

        self.title_label = ctk.CTkLabel(
            header_row,
            text=title.upper(),
            font=Theme.get_font(11, "bold"),
            text_color=Theme.TEXT_MUTED
        )
        self.title_label.pack(side="left")

        self.icon_badge = ctk.CTkLabel(
            header_row,
            text=icon,
            font=Theme.get_font(14, "normal")
        )
        self.icon_badge.pack(side="right")

        # Value Row
        self.value_label = ctk.CTkLabel(
            content,
            text=str(value),
            font=Theme.get_font(24, "bold"),
            text_color=Theme.TEXT_MAIN
        )
        self.value_label.pack(anchor="w", pady=(6, 2))

        # Subtitle Row
        self.subtitle_label = ctk.CTkLabel(
            content,
            text=subtitle,
            font=Theme.get_font(11, "normal"),
            text_color=Theme.TEXT_DIM
        )
        if subtitle:
            self.subtitle_label.pack(anchor="w")

    def update_value(self, new_value: str, subtitle: str = ""):
        self.value_label.configure(text=str(new_value))
        if subtitle:
            self.subtitle_label.configure(text=subtitle)
            if not self.subtitle_label.winfo_ismapped():
                self.subtitle_label.pack(anchor="w")
