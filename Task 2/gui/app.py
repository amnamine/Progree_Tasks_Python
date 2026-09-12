"""Main Modern Tkinter Desktop GUI Application for Fibonacci Generation & Benchmarking."""

import json
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from typing import Any, List, Optional

from fibonacci.benchmark import compare_algorithms, generate_benchmark_report, BenchmarkMetric
from fibonacci.core import (
    fibonacci_sequence,
    fibonacci_nth,
    fibonacci_by_max_value,
    fibonacci_range,
)
from fibonacci.exceptions import (
    FibonacciError,
    InvalidInputError,
    NegativeBoundError,
    RangeBoundError,
)
from fibonacci.validator import sanitize_integer, validate_range_bounds

from .theme import PALETTE, FONTS, draw_rounded_rectangle
from .visualizer import FibonacciVisualizer


class ModernButton(tk.Canvas):
    """Custom styled modern button with hover glow and smooth click animations."""

    def __init__(
        self,
        parent: tk.Widget,
        text: str,
        command: Optional[Any] = None,
        bg_color: str = PALETTE["accent_emerald"],
        hover_color: str = PALETTE["accent_emerald_dark"],
        text_color: str = "#FFFFFF",
        width: int = 140,
        height: int = 38,
        radius: int = 8,
        font: Any = FONTS["body_md"],
        **kwargs,
    ) -> None:
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=parent.cget("bg") if hasattr(parent, "cget") else PALETTE["bg_card"],
            highlightthickness=0,
            **kwargs,
        )
        self.text = text
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.w = width
        self.h = height
        self.radius = radius
        self.font = font
        self.is_hovered = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

        self.draw()

    def draw(self) -> None:
        self.delete("all")
        cur_bg = self.hover_color if self.is_hovered else self.bg_color
        draw_rounded_rectangle(self, 2, 2, self.w - 2, self.h - 2, radius=self.radius, fill=cur_bg, outline="")
        self.create_text(
            self.w // 2,
            self.h // 2,
            text=self.text,
            fill=self.text_color,
            font=self.font,
        )

    def _on_enter(self, event: Any) -> None:
        self.is_hovered = True
        self.config(cursor="hand2")
        self.draw()

    def _on_leave(self, event: Any) -> None:
        self.is_hovered = False
        self.config(cursor="")
        self.draw()

    def _on_click(self, event: Any) -> None:
        if self.command:
            self.command()


class ToastNotification(tk.Frame):
    """Floating modern notification banner."""

    def __init__(self, parent: tk.Widget) -> None:
        super().__init__(parent, bg=PALETTE["bg_card_alt"], highlightthickness=1, highlightbackground=PALETTE["border_emerald"])
        self.label = tk.Label(
            self,
            text="",
            bg=PALETTE["bg_card_alt"],
            fg=PALETTE["text_primary"],
            font=FONTS["body_sm"],
            padx=16,
            pady=8,
        )
        self.label.pack()
        self.hide_job: Optional[str] = None

    def show(self, message: str, duration_ms: int = 2500, is_error: bool = False) -> None:
        if self.hide_job:
            self.after_cancel(self.hide_job)
        
        border_col = PALETTE["accent_rose"] if is_error else PALETTE["border_emerald"]
        text_col = PALETTE["accent_rose"] if is_error else PALETTE["accent_emerald"]
        self.config(highlightbackground=border_col)
        self.label.config(text=message, fg=text_col)

        self.place(relx=0.5, rely=0.92, anchor="center")
        self.lift()
        self.hide_job = self.after(duration_ms, self.hide)

    def hide(self) -> None:
        self.place_forget()


class FibonacciApp(tk.Tk):
    """Main Fibonacci Suite GUI Application."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Fibonacci Algorithmic Suite & Benchmark")
        self.geometry("1100x740")
        self.minsize(980, 640)
        self.configure(bg=PALETTE["bg_main"])

        # State storage
        self.current_sequence: List[int] = []
        self.benchmark_metrics: List[BenchmarkMetric] = []
        self.is_benchmarking = False

        self._setup_styles()
        self._build_header()
        self._build_navigation()
        self._build_content_area()
        self._build_toast()

        # Default tab selection
        self._switch_tab("sequence")

    def _setup_styles(self) -> None:
        """Configures ttk widget styles for dark mode."""
        style = ttk.Style(self)
        style.theme_use("clam")

        # Treeview (Result Table)
        style.configure(
            "Treeview",
            background=PALETTE["bg_card"],
            foreground=PALETTE["text_primary"],
            fieldbackground=PALETTE["bg_card"],
            rowheight=26,
            font=FONTS["mono_sm"],
            borderwidth=0,
        )
        style.configure(
            "Treeview.Heading",
            background=PALETTE["bg_card_alt"],
            foreground=PALETTE["accent_cyan"],
            font=FONTS["title_md"],
            relief="flat",
            padding=6,
        )
        style.map("Treeview", background=[("selected", PALETTE["accent_indigo"])], foreground=[("selected", "#FFFFFF")])

        # Scrollbar
        style.configure(
            "Vertical.TScrollbar",
            background=PALETTE["bg_card_alt"],
            troughcolor=PALETTE["bg_card"],
            bordercolor=PALETTE["border_subtle"],
            arrowcolor=PALETTE["text_secondary"],
        )

        # Combobox
        style.configure(
            "TCombobox",
            background=PALETTE["bg_card_alt"],
            foreground=PALETTE["text_primary"],
            fieldbackground=PALETTE["bg_card_alt"],
            bordercolor=PALETTE["border_subtle"],
            darkcolor=PALETTE["bg_card_alt"],
            lightcolor=PALETTE["bg_card_alt"],
            arrowcolor=PALETTE["accent_cyan"],
        )

    def _build_header(self) -> None:
        header_frame = tk.Frame(self, bg=PALETTE["bg_main"], padx=24, pady=14)
        header_frame.pack(fill="x")

        title_box = tk.Frame(header_frame, bg=PALETTE["bg_main"])
        title_box.pack(side="left")

        title_lbl = tk.Label(
            title_box,
            text="FIBONACCI CORE ALGORITHMIC ENGINE",
            bg=PALETTE["bg_main"],
            fg=PALETTE["text_primary"],
            font=FONTS["title_xl"],
        )
        title_lbl.pack(anchor="w")

        subtitle_lbl = tk.Label(
            title_box,
            text="Exact Sequence Generation • Bound Sanitization • timeit Performance Benchmarking",
            bg=PALETTE["bg_main"],
            fg=PALETTE["text_secondary"],
            font=FONTS["body_sm"],
        )
        subtitle_lbl.pack(anchor="w")

        # Status badge
        badge_frame = tk.Frame(
            header_frame,
            bg=PALETTE["bg_card"],
            padx=12,
            pady=6,
            highlightthickness=1,
            highlightbackground=PALETTE["border_emerald"],
        )
        badge_frame.pack(side="right")
        tk.Label(
            badge_frame,
            text="● ENGINE ACTIVE | v2.0",
            bg=PALETTE["bg_card"],
            fg=PALETTE["accent_emerald"],
            font=FONTS["tag"],
        ).pack()

    def _build_navigation(self) -> None:
        """Builds modern horizontal segmented tab switcher."""
        nav_container = tk.Frame(self, bg=PALETTE["bg_main"], padx=24, pady=4)
        nav_container.pack(fill="x")

        self.nav_card = tk.Frame(
            nav_container,
            bg=PALETTE["bg_card"],
            padx=4,
            pady=4,
            highlightthickness=1,
            highlightbackground=PALETTE["border_subtle"],
        )
        self.nav_card.pack(fill="x")

        self.tab_buttons: dict[str, tk.Label] = {}
        tabs = [
            ("sequence", "⚡ Sequence Engine"),
            ("nth_calc", "🔍 Nth Exact Calculator"),
            ("benchmark", "📊 timeit Benchmark Lab"),
            ("visualizer", "🌀 Spiral & Golden Ratio"),
        ]

        for tab_id, label_text in tabs:
            lbl = tk.Label(
                self.nav_card,
                text=label_text,
                bg=PALETTE["bg_card"],
                fg=PALETTE["text_secondary"],
                font=FONTS["body_md"],
                padx=16,
                pady=8,
                cursor="hand2",
            )
            lbl.pack(side="left", padx=4)
            lbl.bind("<Button-1>", lambda e, tid=tab_id: self._switch_tab(tid))
            self.tab_buttons[tab_id] = lbl

    def _switch_tab(self, active_tab: str) -> None:
        for tid, lbl in self.tab_buttons.items():
            if tid == active_tab:
                lbl.config(bg=PALETTE["accent_indigo"], fg="#FFFFFF", font=FONTS["title_md"])
            else:
                lbl.config(bg=PALETTE["bg_card"], fg=PALETTE["text_secondary"], font=FONTS["body_md"])

        for tid, frame in self.tab_frames.items():
            if tid == active_tab:
                frame.pack(fill="both", expand=True, padx=24, pady=12)
                if tid == "visualizer":
                    self.visualizer.redraw()
            else:
                frame.pack_forget()

    def _build_content_area(self) -> None:
        self.content_container = tk.Frame(self, bg=PALETTE["bg_main"])
        self.content_container.pack(fill="both", expand=True)

        self.tab_frames: dict[str, tk.Frame] = {}

        # Build each tab view
        self._build_sequence_tab()
        self._build_nth_tab()
        self._build_benchmark_tab()
        self._build_visualizer_tab()

    # =========================================================================
    # TAB 1: SEQUENCE GENERATION ENGINE
    # =========================================================================
    def _build_sequence_tab(self) -> None:
        frame = tk.Frame(self.content_container, bg=PALETTE["bg_main"])
        self.tab_frames["sequence"] = frame

        # Top Control Card
        ctrl_card = tk.Frame(
            frame,
            bg=PALETTE["bg_card"],
            padx=18,
            pady=16,
            highlightthickness=1,
            highlightbackground=PALETTE["border_subtle"],
        )
        ctrl_card.pack(fill="x", pady=(0, 12))

        # Controls Grid
        row1 = tk.Frame(ctrl_card, bg=PALETTE["bg_card"])
        row1.pack(fill="x", pady=4)

        # Mode Selection
        tk.Label(row1, text="Generation Mode:", bg=PALETTE["bg_card"], fg=PALETTE["text_secondary"], font=FONTS["body_md"]).pack(side="left", padx=(0, 8))
        self.seq_mode_var = tk.StringVar(value="Range [Start, End]")
        mode_cb = ttk.Combobox(
            row1,
            textvariable=self.seq_mode_var,
            values=["Range [Start, End]", "First N Terms", "Value Ceiling (<= Max)"],
            state="readonly",
            width=22,
        )
        mode_cb.pack(side="left", padx=(0, 20))
        mode_cb.bind("<<ComboboxSelected>>", self._on_seq_mode_change)

        # Input Start / End
        self.start_lbl = tk.Label(row1, text="Start Index:", bg=PALETTE["bg_card"], fg=PALETTE["text_secondary"], font=FONTS["body_md"])
        self.start_lbl.pack(side="left", padx=(0, 4))
        self.start_entry = tk.Entry(row1, width=8, bg=PALETTE["bg_card_alt"], fg=PALETTE["text_primary"], insertbackground="#FFF", font=FONTS["mono_md"], relief="flat", highlightthickness=1, highlightbackground=PALETTE["border_subtle"])
        self.start_entry.insert(0, "0")
        self.start_entry.pack(side="left", padx=(0, 16))

        self.end_lbl = tk.Label(row1, text="End Index:", bg=PALETTE["bg_card"], fg=PALETTE["text_secondary"], font=FONTS["body_md"])
        self.end_lbl.pack(side="left", padx=(0, 4))
        self.end_entry = tk.Entry(row1, width=10, bg=PALETTE["bg_card_alt"], fg=PALETTE["text_primary"], insertbackground="#FFF", font=FONTS["mono_md"], relief="flat", highlightthickness=1, highlightbackground=PALETTE["border_subtle"])
        self.end_entry.insert(0, "20")
        self.end_entry.pack(side="left", padx=(0, 20))

        # Algorithm method
        tk.Label(row1, text="Algorithm:", bg=PALETTE["bg_card"], fg=PALETTE["text_secondary"], font=FONTS["body_md"]).pack(side="left", padx=(0, 4))
        self.seq_algo_var = tk.StringVar(value="iterative")
        algo_cb = ttk.Combobox(
            row1,
            textvariable=self.seq_algo_var,
            values=["iterative", "fast_doubling", "matrix", "memoized"],
            state="readonly",
            width=14,
        )
        algo_cb.pack(side="left", padx=(0, 16))

        # Button Row
        row2 = tk.Frame(ctrl_card, bg=PALETTE["bg_card"])
        row2.pack(fill="x", pady=(12, 0))

        ModernButton(row2, text="⚡ Generate Sequence", command=self._generate_sequence, bg_color=PALETTE["accent_emerald"], hover_color=PALETTE["accent_emerald_dark"], width=170).pack(side="left", padx=(0, 10))
        ModernButton(row2, text="📋 Copy List", command=self._copy_sequence, bg_color=PALETTE["accent_indigo"], hover_color="#4F46E5", width=120).pack(side="left", padx=(0, 10))
        ModernButton(row2, text="💾 Export JSON/CSV", command=self._export_sequence, bg_color=PALETTE["bg_card_alt"], hover_color=PALETTE["bg_card_hover"], width=150).pack(side="left", padx=(0, 10))
        ModernButton(row2, text="🧹 Clear", command=self._clear_sequence, bg_color=PALETTE["bg_card_alt"], hover_color=PALETTE["bg_card_hover"], width=90).pack(side="left")

        # Stats Bar Card
        self.seq_stats_frame = tk.Frame(frame, bg=PALETTE["bg_card_alt"], padx=16, pady=8, highlightthickness=1, highlightbackground=PALETTE["border_subtle"])
        self.seq_stats_frame.pack(fill="x", pady=(0, 8))
        self.seq_stats_lbl = tk.Label(
            self.seq_stats_frame,
            text="Ready. Enter sequence bounds and click 'Generate Sequence'.",
            bg=PALETTE["bg_card_alt"],
            fg=PALETTE["text_secondary"],
            font=FONTS["body_sm"],
        )
        self.seq_stats_lbl.pack(anchor="w")

        # Result Table View
        table_card = tk.Frame(frame, bg=PALETTE["bg_card"], highlightthickness=1, highlightbackground=PALETTE["border_subtle"])
        table_card.pack(fill="both", expand=True)

        columns = ("index", "notation", "value", "digits")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")
        self.tree.heading("index", text="# Index")
        self.tree.heading("notation", text="Symbol")
        self.tree.heading("value", text="Exact Value F(n)")
        self.tree.heading("digits", text="Digits")

        self.tree.column("index", width=90, anchor="center")
        self.tree.column("notation", width=110, anchor="center")
        self.tree.column("value", width=620, anchor="w")
        self.tree.column("digits", width=90, anchor="center")

        scrollbar = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        scrollbar.pack(side="right", fill="y", pady=2)

    def _on_seq_mode_change(self, event: Any = None) -> None:
        mode = self.seq_mode_var.get()
        if mode == "Range [Start, End]":
            self.start_lbl.pack(side="left", padx=(0, 4))
            self.start_entry.pack(side="left", padx=(0, 16))
            self.end_lbl.config(text="End Index:")
        elif mode == "First N Terms":
            self.start_lbl.pack_forget()
            self.start_entry.pack_forget()
            self.end_lbl.config(text="Count (N):")
        else:  # Value Ceiling
            self.start_lbl.pack_forget()
            self.start_entry.pack_forget()
            self.end_lbl.config(text="Max Value Limit:")

    def _generate_sequence(self) -> None:
        mode = self.seq_mode_var.get()
        method = self.seq_algo_var.get()

        try:
            start_time = time.perf_counter()

            if mode == "Range [Start, End]":
                start_val = self.start_entry.get()
                end_val = self.end_entry.get()
                start_clean, end_clean = validate_range_bounds(start_val, end_val)
                seq = fibonacci_sequence(end_clean, start_bound=start_clean, method=method)
                indices = list(range(start_clean, end_clean + 1))
            elif mode == "First N Terms":
                count_val = self.end_entry.get()
                count_clean = sanitize_integer(count_val, param_name="count", allow_negative=False)
                if count_clean == 0:
                    seq = []
                    indices = []
                else:
                    seq = fibonacci_sequence(count_clean - 1, start_bound=0, method=method)
                    indices = list(range(len(seq)))
            else:  # Value Ceiling
                max_val = self.end_entry.get()
                seq = fibonacci_by_max_value(max_val)
                indices = list(range(len(seq)))

            elapsed = time.perf_counter() - start_time
            self.current_sequence = seq

            # Populate Treeview
            self.tree.delete(*self.tree.get_children())
            for idx, val in zip(indices, seq):
                val_str = str(val)
                digits = len(val_str)
                display_val = val_str if digits <= 70 else f"{val_str[:35]}...{val_str[-35:]}"
                self.tree.insert("", "end", values=(idx, f"F({idx})", display_val, digits))

            # Format execution time
            time_str = f"{elapsed*1e6:.2f} µs" if elapsed < 1e-3 else f"{elapsed*1e3:.3f} ms"
            max_num_digits = len(str(seq[-1])) if seq else 0

            self.seq_stats_lbl.config(
                text=f"✓ Generated {len(seq):,} terms in {time_str} | Algorithm: {method} | Max Term: F({indices[-1] if indices else 0}) with {max_num_digits} digits",
                fg=PALETTE["accent_emerald"],
            )
            self._toast(f"Generated {len(seq):,} Fibonacci numbers successfully!")

        except FibonacciError as err:
            self.seq_stats_lbl.config(text=f"⚠ Validation Error: {err.message}", fg=PALETTE["accent_rose"])
            self._toast(str(err.message), is_error=True)
        except Exception as err:
            self.seq_stats_lbl.config(text=f"⚠ Unexpected Error: {err}", fg=PALETTE["accent_rose"])
            self._toast(f"Error: {err}", is_error=True)

    def _copy_sequence(self) -> None:
        if not self.current_sequence:
            self._toast("No sequence generated to copy!", is_error=True)
            return
        json_str = json.dumps(self.current_sequence)
        self.clipboard_clear()
        self.clipboard_append(json_str)
        self._toast(f"Copied {len(self.current_sequence):,} numbers to clipboard!")

    def _export_sequence(self) -> None:
        if not self.current_sequence:
            self._toast("No sequence data to export!", is_error=True)
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json"), ("CSV Files", "*.csv"), ("Text Files", "*.txt")],
            title="Export Fibonacci Sequence",
        )
        if not path:
            return

        try:
            if path.endswith(".json"):
                with open(path, "w", encoding="utf-8") as f:
                    json.dump({"count": len(self.current_sequence), "sequence": self.current_sequence}, f, indent=2)
            elif path.endswith(".csv"):
                with open(path, "w", encoding="utf-8") as f:
                    f.write("Index,Symbol,Value\n")
                    for i, val in enumerate(self.current_sequence):
                        f.write(f"{i},F({i}),{val}\n")
            else:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("\n".join(str(v) for v in self.current_sequence))
            self._toast(f"Exported successfully to {path.split('/')[-1]}")
        except Exception as err:
            self._toast(f"Export failed: {err}", is_error=True)

    def _clear_sequence(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.current_sequence = []
        self.seq_stats_lbl.config(text="Cleared.", fg=PALETTE["text_secondary"])

    # =========================================================================
    # TAB 2: EXACT NTH FIBONACCI CALCULATOR
    # =========================================================================
    def _build_nth_tab(self) -> None:
        frame = tk.Frame(self.content_container, bg=PALETTE["bg_main"])
        self.tab_frames["nth_calc"] = frame

        card = tk.Frame(
            frame,
            bg=PALETTE["bg_card"],
            padx=20,
            pady=20,
            highlightthickness=1,
            highlightbackground=PALETTE["border_subtle"],
        )
        card.pack(fill="x", pady=(0, 12))

        row1 = tk.Frame(card, bg=PALETTE["bg_card"])
        row1.pack(fill="x", pady=4)

        tk.Label(row1, text="Target Index (N):", bg=PALETTE["bg_card"], fg=PALETTE["text_secondary"], font=FONTS["title_md"]).pack(side="left", padx=(0, 8))
        self.nth_input = tk.Entry(row1, width=14, bg=PALETTE["bg_card_alt"], fg=PALETTE["text_primary"], font=FONTS["mono_lg"], insertbackground="#FFF", relief="flat", highlightthickness=1, highlightbackground=PALETTE["border_subtle"])
        self.nth_input.insert(0, "100")
        self.nth_input.pack(side="left", padx=(0, 20))

        tk.Label(row1, text="Method:", bg=PALETTE["bg_card"], fg=PALETTE["text_secondary"], font=FONTS["body_md"]).pack(side="left", padx=(0, 6))
        self.nth_algo_var = tk.StringVar(value="fast_doubling")
        cb = ttk.Combobox(row1, textvariable=self.nth_algo_var, values=["fast_doubling", "matrix", "iterative", "memoized"], state="readonly", width=16)
        cb.pack(side="left", padx=(0, 20))

        ModernButton(row1, text="⚡ Compute F(n)", command=self._compute_nth, bg_color=PALETTE["accent_cyan"], hover_color="#0891B2", width=150).pack(side="left")

        # Quick preset pills
        preset_row = tk.Frame(card, bg=PALETTE["bg_card"])
        preset_row.pack(fill="x", pady=(12, 0))
        tk.Label(preset_row, text="Presets:", bg=PALETTE["bg_card"], fg=PALETTE["text_muted"], font=FONTS["tag"]).pack(side="left", padx=(0, 8))
        for p_val in [10, 50, 100, 500, 1000, 5000, 10000]:
            btn = tk.Label(preset_row, text=f"n={p_val:,}", bg=PALETTE["bg_card_alt"], fg=PALETTE["accent_cyan"], font=FONTS["tag"], padx=8, pady=3, cursor="hand2")
            btn.pack(side="left", padx=4)
            btn.bind("<Button-1>", lambda e, val=p_val: self._set_nth_preset(val))

        # Result Metadata Card
        self.nth_meta_card = tk.Frame(frame, bg=PALETTE["bg_card_alt"], padx=18, pady=12, highlightthickness=1, highlightbackground=PALETTE["border_subtle"])
        self.nth_meta_card.pack(fill="x", pady=(0, 12))

        self.nth_meta_lbl = tk.Label(
            self.nth_meta_card,
            text="Enter index N (e.g. 1000) and click Compute.",
            bg=PALETTE["bg_card_alt"],
            fg=PALETTE["text_secondary"],
            font=FONTS["body_md"],
        )
        self.nth_meta_lbl.pack(anchor="w")

        # Big Integer Output Text Box
        box_card = tk.Frame(frame, bg=PALETTE["bg_card"], highlightthickness=1, highlightbackground=PALETTE["border_subtle"])
        box_card.pack(fill="both", expand=True)

        self.nth_textbox = tk.Text(
            box_card,
            bg=PALETTE["bg_card"],
            fg=PALETTE["text_primary"],
            font=FONTS["mono_md"],
            insertbackground="#FFF",
            wrap="char",
            relief="flat",
            padx=12,
            pady=12,
        )
        scroll = ttk.Scrollbar(box_card, orient="vertical", command=self.nth_textbox.yview)
        self.nth_textbox.configure(yscrollcommand=scroll.set)

        self.nth_textbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _set_nth_preset(self, val: int) -> None:
        self.nth_input.delete(0, "end")
        self.nth_input.insert(0, str(val))
        self._compute_nth()

    def _compute_nth(self) -> None:
        raw = self.nth_input.get()
        method = self.nth_algo_var.get()

        try:
            n_clean = sanitize_integer(raw, param_name="N", allow_negative=False)
            start_t = time.perf_counter()
            val = fibonacci_nth(n_clean, method=method)
            calc_t = time.perf_counter() - start_t

            val_str = str(val)
            digits = len(val_str)
            time_str = f"{calc_t*1e6:.2f} µs" if calc_t < 1e-3 else f"{calc_t*1e3:.3f} ms"

            self.nth_meta_lbl.config(
                text=f"✓ Calculated F({n_clean:,}) using {method} in {time_str} | Total Exact Digits: {digits:,}",
                fg=PALETTE["accent_emerald"],
            )

            self.nth_textbox.delete("1.0", "end")
            self.nth_textbox.insert("1.0", val_str)
            self._toast(f"Calculated F({n_clean:,}) ({digits:,} digits)")
        except FibonacciError as err:
            self.nth_meta_lbl.config(text=f"⚠ Validation Error: {err.message}", fg=PALETTE["accent_rose"])
            self._toast(str(err.message), is_error=True)
        except Exception as err:
            self.nth_meta_lbl.config(text=f"⚠ Calculation Error: {err}", fg=PALETTE["accent_rose"])
            self._toast(f"Error: {err}", is_error=True)

    # =========================================================================
    # TAB 3: TIMEIT BENCHMARK LABORATORY
    # =========================================================================
    def _build_benchmark_tab(self) -> None:
        frame = tk.Frame(self.content_container, bg=PALETTE["bg_main"])
        self.tab_frames["benchmark"] = frame

        card = tk.Frame(
            frame,
            bg=PALETTE["bg_card"],
            padx=18,
            pady=16,
            highlightthickness=1,
            highlightbackground=PALETTE["border_subtle"],
        )
        card.pack(fill="x", pady=(0, 12))

        row1 = tk.Frame(card, bg=PALETTE["bg_card"])
        row1.pack(fill="x")

        tk.Label(row1, text="Test Bound (N):", bg=PALETTE["bg_card"], fg=PALETTE["text_secondary"], font=FONTS["body_md"]).pack(side="left", padx=(0, 6))
        self.bench_n_input = tk.Entry(row1, width=10, bg=PALETTE["bg_card_alt"], fg=PALETTE["text_primary"], font=FONTS["mono_md"], insertbackground="#FFF", relief="flat", highlightthickness=1, highlightbackground=PALETTE["border_subtle"])
        self.bench_n_input.insert(0, "150")
        self.bench_n_input.pack(side="left", padx=(0, 16))

        tk.Label(row1, text="Loops/Batch:", bg=PALETTE["bg_card"], fg=PALETTE["text_secondary"], font=FONTS["body_md"]).pack(side="left", padx=(0, 6))
        self.bench_iter_input = tk.Entry(row1, width=8, bg=PALETTE["bg_card_alt"], fg=PALETTE["text_primary"], font=FONTS["mono_md"], insertbackground="#FFF", relief="flat", highlightthickness=1, highlightbackground=PALETTE["border_subtle"])
        self.bench_iter_input.insert(0, "500")
        self.bench_iter_input.pack(side="left", padx=(0, 16))

        tk.Label(row1, text="Repeat Trials:", bg=PALETTE["bg_card"], fg=PALETTE["text_secondary"], font=FONTS["body_md"]).pack(side="left", padx=(0, 6))
        self.bench_rep_input = tk.Entry(row1, width=6, bg=PALETTE["bg_card_alt"], fg=PALETTE["text_primary"], font=FONTS["mono_md"], insertbackground="#FFF", relief="flat", highlightthickness=1, highlightbackground=PALETTE["border_subtle"])
        self.bench_rep_input.insert(0, "5")
        self.bench_rep_input.pack(side="left", padx=(0, 20))

        ModernButton(row1, text="🚀 Run timeit Benchmarks", command=self._start_benchmark, bg_color=PALETTE["accent_violet"], hover_color="#7C3AED", width=210).pack(side="left", padx=(0, 10))
        ModernButton(row1, text="📋 Copy Report", command=self._copy_benchmark_report, bg_color=PALETTE["bg_card_alt"], hover_color=PALETTE["bg_card_hover"], width=130).pack(side="left")

        # Benchmark Leaderboard Table
        table_card = tk.Frame(frame, bg=PALETTE["bg_card"], highlightthickness=1, highlightbackground=PALETTE["border_subtle"])
        table_card.pack(fill="both", expand=True)

        cols = ("rank", "algo", "mean_time", "min_time", "stdev", "ops_sec")
        self.bench_tree = ttk.Treeview(table_card, columns=cols, show="headings", selectmode="browse")
        self.bench_tree.heading("rank", text="Rank")
        self.bench_tree.heading("algo", text="Algorithm Name")
        self.bench_tree.heading("mean_time", text="Mean Execution Time")
        self.bench_tree.heading("min_time", text="Best (Min) Time")
        self.bench_tree.heading("stdev", text="Std Deviation")
        self.bench_tree.heading("ops_sec", text="Throughput (Ops/sec)")

        self.bench_tree.column("rank", width=60, anchor="center")
        self.bench_tree.column("algo", width=220, anchor="w")
        self.bench_tree.column("mean_time", width=160, anchor="center")
        self.bench_tree.column("min_time", width=140, anchor="center")
        self.bench_tree.column("stdev", width=140, anchor="center")
        self.bench_tree.column("ops_sec", width=180, anchor="e")

        self.bench_tree.pack(fill="both", expand=True, padx=2, pady=2)

    def _start_benchmark(self) -> None:
        if self.is_benchmarking:
            return

        try:
            n_clean = sanitize_integer(self.bench_n_input.get(), param_name="N", allow_negative=False)
            iter_clean = sanitize_integer(self.bench_iter_input.get(), param_name="Loops", allow_negative=False, min_value=1)
            rep_clean = sanitize_integer(self.bench_rep_input.get(), param_name="Repeat", allow_negative=False, min_value=1)
        except FibonacciError as err:
            self._toast(err.message, is_error=True)
            return

        self.is_benchmarking = True
        self._toast(f"Running timeit benchmarks for N={n_clean}...")

        # Run benchmark asynchronously so Tkinter never stutters
        def worker() -> None:
            try:
                metrics = compare_algorithms(n_clean, number=iter_clean, repeat=rep_clean)
                self.benchmark_metrics = metrics
                self.after(0, self._render_benchmark_results)
            except Exception as err:
                self.after(0, lambda: self._toast(f"Benchmark error: {err}", is_error=True))
            finally:
                self.is_benchmarking = False

        threading.Thread(target=worker, daemon=True).start()

    def _render_benchmark_results(self) -> None:
        self.bench_tree.delete(*self.bench_tree.get_children())
        for idx, m in enumerate(self.benchmark_metrics, start=1):
            rank_badge = f"🏆 #{idx}" if idx == 1 else f"#{idx}"
            self.bench_tree.insert(
                "",
                "end",
                values=(
                    rank_badge,
                    m.algorithm_name,
                    m.formatted_mean,
                    m._format_time(m.min_seconds),
                    m._format_time(m.stdev_seconds),
                    f"{m.ops_per_second:,.1f}",
                ),
            )
        self._toast("timeit benchmarks completed successfully!")

    def _copy_benchmark_report(self) -> None:
        if not self.benchmark_metrics:
            self._toast("No benchmark results to copy!", is_error=True)
            return
        report = generate_benchmark_report(self.benchmark_metrics)
        self.clipboard_clear()
        self.clipboard_append(report)
        self._toast("Copied ASCII benchmark report to clipboard!")

    # =========================================================================
    # TAB 4: VISUALIZER (SPIRAL & GOLDEN RATIO)
    # =========================================================================
    def _build_visualizer_tab(self) -> None:
        frame = tk.Frame(self.content_container, bg=PALETTE["bg_main"])
        self.tab_frames["visualizer"] = frame

        ctrl_bar = tk.Frame(
            frame,
            bg=PALETTE["bg_card"],
            padx=16,
            pady=12,
            highlightthickness=1,
            highlightbackground=PALETTE["border_subtle"],
        )
        ctrl_bar.pack(fill="x", pady=(0, 10))

        # Canvas Area
        self.visualizer = FibonacciVisualizer(frame)

        # Mode toggle
        ModernButton(ctrl_bar, text="🌀 Golden Spiral", command=lambda: self.visualizer.set_mode("spiral"), bg_color=PALETTE["accent_emerald"], hover_color=PALETTE["accent_emerald_dark"], width=140).pack(side="left", padx=(0, 8))
        ModernButton(ctrl_bar, text="📈 Ratio Convergence (φ)", command=lambda: self.visualizer.set_mode("convergence"), bg_color=PALETTE["accent_cyan"], hover_color="#0891B2", width=190).pack(side="left", padx=(0, 20))

        # Animation controls
        ModernButton(ctrl_bar, text="▶ Play", command=lambda: self.visualizer.start_animation(max_steps=12), bg_color=PALETTE["accent_indigo"], hover_color="#4F46E5", width=90).pack(side="left", padx=(0, 6))
        ModernButton(ctrl_bar, text="⏸ Pause", command=lambda: self.visualizer.stop_animation(), bg_color=PALETTE["bg_card_alt"], hover_color=PALETTE["bg_card_hover"], width=90).pack(side="left", padx=(0, 6))
        ModernButton(ctrl_bar, text="⏮ Back", command=lambda: self.visualizer.step_backward(), bg_color=PALETTE["bg_card_alt"], hover_color=PALETTE["bg_card_hover"], width=80).pack(side="left", padx=(0, 6))
        ModernButton(ctrl_bar, text="⏭ Next", command=lambda: self.visualizer.step_forward(), bg_color=PALETTE["bg_card_alt"], hover_color=PALETTE["bg_card_hover"], width=80).pack(side="left", padx=(0, 6))
        ModernButton(ctrl_bar, text="🔄 Reset", command=lambda: self.visualizer.reset(), bg_color=PALETTE["bg_card_alt"], hover_color=PALETTE["bg_card_hover"], width=80).pack(side="left")

        self.visualizer.pack(fill="both", expand=True)
        self.visualizer.reset()

    def _build_toast(self) -> None:
        self.toast = ToastNotification(self)

    def _toast(self, msg: str, is_error: bool = False) -> None:
        self.toast.show(msg, is_error=is_error)


def launch_app() -> None:
    """Launches modern Tkinter Desktop Application."""
    app = FibonacciApp()
    app.mainloop()


if __name__ == "__main__":
    launch_app()
