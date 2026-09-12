"""
Toast Notification Component.
Smooth popup notification banner with status icons and auto-dismiss.
"""

import customtkinter as ctk
from ui.theme import Theme


class ToastNotification(ctk.CTkFrame):
    def __init__(self, master, message: str, toast_type: str = "success", duration_ms: int = 3500):
        color_map = {
            "success": (Theme.ACCENT_EMERALD, "✓"),
            "error": (Theme.ACCENT_ROSE, "✕"),
            "warn": (Theme.ACCENT_AMBER, "⚠"),
            "info": (Theme.ACCENT_CYAN, "ℹ")
        }
        accent, icon_char = color_map.get(toast_type.lower(), (Theme.ACCENT_PRIMARY, "ℹ"))

        super().__init__(
            master,
            fg_color=Theme.BG_CARD,
            border_width=1,
            border_color=accent,
            corner_radius=Theme.RADIUS_PILL
        )

        # Icon
        icon_lbl = ctk.CTkLabel(
            self,
            text=icon_char,
            font=Theme.get_font(13, "bold"),
            text_color=accent,
            width=20
        )
        icon_lbl.pack(side="left", padx=(12, 6), pady=8)

        # Message
        msg_lbl = ctk.CTkLabel(
            self,
            text=message,
            font=Theme.get_font(12, "normal"),
            text_color=Theme.TEXT_MAIN
        )
        msg_lbl.pack(side="left", padx=(0, 16), pady=8)

        # Position at bottom-center
        self.place(relx=0.5, rely=0.92, anchor="center")

        # Auto dismiss
        self.after(duration_ms, self._dismiss)

    def _dismiss(self):
        try:
            self.destroy()
        except Exception:
            pass


def show_toast(master, message: str, toast_type: str = "success"):
    return ToastNotification(master, message, toast_type)
