"""Design system, modern dark palette, typography tokens, and canvas styling helpers."""

from typing import Any, Tuple

# Modern Dark Glassmorphic Color Palette
PALETTE = {
    "bg_main": "#0B0F19",          # Deepest slate-navy background
    "bg_card": "#111827",          # Primary card surface
    "bg_card_alt": "#1F2937",      # Secondary elevated card
    "bg_card_hover": "#374151",    # Hover surface
    "border_subtle": "#1F293D",    # Subtle card outline
    "border_active": "#3B82F6",    # Active glowing outline
    "border_emerald": "#10B981",   # Success/Emerald highlight
    
    # Text colors
    "text_primary": "#F9FAFB",     # Crisp white
    "text_secondary": "#9CA3AF",   # Muted gray
    "text_muted": "#6B7280",       # Dark gray
    
    # Accent Colors
    "accent_emerald": "#10B981",   # Primary green
    "accent_emerald_dark": "#059669",
    "accent_cyan": "#06B6D4",      # Vibrant cyan
    "accent_blue": "#3B82F6",      # Royal blue
    "accent_indigo": "#6366F1",    # Indigo
    "accent_violet": "#8B5CF6",    # Purple
    "accent_amber": "#F59E0B",     # Warning / gold
    "accent_rose": "#F43F5E",      # Error / crimson
    
    # Graph & Spiral Colors
    "spiral_colors": [
        "#3B82F6", "#06B6D4", "#10B981", "#84CC16", 
        "#EAB308", "#F97316", "#EF4444", "#EC4899", 
        "#8B5CF6", "#6366F1"
    ]
}

# Typography Tokens
FONTS = {
    "title_xl": ("Segoe UI", 18, "bold"),
    "title_lg": ("Segoe UI", 14, "bold"),
    "title_md": ("Segoe UI", 11, "bold"),
    "body_lg": ("Segoe UI", 11),
    "body_md": ("Segoe UI", 10),
    "body_sm": ("Segoe UI", 9),
    "mono_lg": ("Consolas", 12, "bold"),
    "mono_md": ("Consolas", 10),
    "mono_sm": ("Consolas", 9),
    "tag": ("Segoe UI", 8, "bold"),
}


def draw_rounded_rectangle(
    canvas: Any,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    radius: int = 12,
    **kwargs: Any,
) -> int:
    """Draws a smooth rounded rectangle on a Tkinter Canvas."""
    points = [
        x1 + radius, y1,
        x1 + radius, y1,
        x2 - radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)
