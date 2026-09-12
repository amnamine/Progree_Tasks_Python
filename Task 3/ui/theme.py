"""
Modern Theme & UI Style Guide.
Curated dark and light palettes, typography, and geometry tokens.
"""

class Theme:
    # Mode
    APPEARANCE_MODE = "Dark" # "Dark" or "Light"
    COLOR_THEME = "blue"

    # Color Palette (Deep Slate / Obsidian + Vivid Accents)
    BG_DARK = "#0F172A"         # Slate 900
    BG_CARD = "#1E293B"         # Slate 800
    BG_CARD_HOVER = "#334155"   # Slate 700
    BG_SIDEBAR = "#0B1120"      # Slate 950
    BG_INPUT = "#1E293B"        # Slate 800
    BG_LOG = "#050811"          # Deep Black Terminal

    # Primary Accents
    ACCENT_PRIMARY = "#6366F1"    # Indigo 500
    ACCENT_HOVER = "#4F46E5"      # Indigo 600
    ACCENT_CYAN = "#06B6D4"       # Cyan 500
    ACCENT_EMERALD = "#10B981"    # Emerald 500
    ACCENT_ROSE = "#F43F5E"       # Rose 500
    ACCENT_AMBER = "#F59E0B"      # Amber 500
    ACCENT_PURPLE = "#8B5CF6"     # Purple 500

    # Borders & Dividers
    BORDER_SUBTLE = "#334155"
    BORDER_ACTIVE = "#6366F1"
    BORDER_GLOW = "#38BDF8"

    # Typography Colors
    TEXT_MAIN = "#F8FAFC"
    TEXT_MUTED = "#94A3B8"
    TEXT_DIM = "#64748B"
    TEXT_ACCENT = "#38BDF8"

    # Log Terminal Colors
    LOG_INFO = "#38BDF8"       # Sky Blue
    LOG_SUCCESS = "#34D399"    # Emerald Green
    LOG_WARN = "#FBBF24"       # Amber
    LOG_ERROR = "#F87171"      # Red
    LOG_DEBUG = "#A78BFA"      # Light Purple

    # Geometry & Radiuses
    RADIUS_SMALL = 6
    RADIUS_MEDIUM = 10
    RADIUS_LARGE = 14
    RADIUS_PILL = 20

    # Fonts
    FONT_FAMILY = "Segoe UI"
    FONT_MONO = "Consolas"

    @classmethod
    def get_font(cls, size: int = 13, weight: str = "normal", mono: bool = False) -> tuple:
        family = cls.FONT_MONO if mono else cls.FONT_FAMILY
        return (family, size, weight)
