"""
Ultra-Modern Tkinter GUI for Nexus Hybrid AI Chatbot.
Features luxury dark aesthetics, animated typing indicator,
rich bubble cards, dynamic quick pills, live session inspector,
thread-safe background AI execution, audio feedback, and export tools.
"""

import os
import sys
import time
import json
import threading
from typing import Dict, Any, List, Optional, Tuple, Callable
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False

from config import (
    THEME, BOT_NAME, BOT_VERSION, BOT_TAGLINE,
    AVAILABLE_MODELS, DEFAULT_MODEL, GROQ_API_KEY
)
from hybrid_chatbot import HybridChatbot


class ModernChatBubble(tk.Frame):
    """Custom styled chat message card with avatars, badges, and copy action."""

    def __init__(self, parent, role: str, content: str, timestamp: str, source: str = "Rule Engine", on_copy=None, **kwargs):
        super().__init__(parent, bg=THEME["bg_chat"], **kwargs)
        self.role = role
        self.content = content
        self.timestamp = timestamp
        self.source = source
        self.on_copy = on_copy

        self._build_ui()

    def _build_ui(self):
        is_user = (self.role == "user")
        align = "e" if is_user else "w"
        bubble_bg = THEME["user_bubble"] if is_user else THEME["bot_bubble"]
        text_color = THEME["user_text"] if is_user else THEME["bot_text"]
        border_color = THEME["user_bubble_border"] if is_user else THEME["bot_bubble_border"]

        # Outer wrapper frame for alignment
        wrapper = tk.Frame(self, bg=THEME["bg_chat"])
        wrapper.pack(fill="x", padx=14, pady=6, anchor=align)

        # Bubble Card Frame
        card = tk.Frame(
            wrapper,
            bg=bubble_bg,
            highlightbackground=border_color,
            highlightthickness=1,
            padx=12,
            pady=10
        )
        card.pack(anchor=align, padx=(60 if is_user else 0, 0 if is_user else 60))

        # Header: Avatar + Name + Source Badge + Time
        header_frame = tk.Frame(card, bg=bubble_bg)
        header_frame.pack(fill="x", pady=(0, 6))

        avatar = "👤 You" if is_user else "🤖 Nexus AI"
        avatar_lbl = tk.Label(
            header_frame,
            text=avatar,
            font=(THEME["font_family"], 9, "bold"),
            fg="#ffffff" if is_user else THEME["accent_light"],
            bg=bubble_bg
        )
        avatar_lbl.pack(side="left")

        if not is_user:
            # Source Tag
            src_bg = "#065f46" if "Rule" in self.source else "#4338ca"
            src_lbl = tk.Label(
                header_frame,
                text=f" {self.source} ",
                font=(THEME["font_family"], 8, "bold"),
                fg="#ffffff",
                bg=src_bg,
                padx=4,
                pady=1
            )
            src_lbl.pack(side="left", padx=8)

        # Timestamp
        time_lbl = tk.Label(
            header_frame,
            text=self.timestamp,
            font=(THEME["font_family"], 8),
            fg="#cbd5e1" if is_user else THEME["text_muted"],
            bg=bubble_bg
        )
        time_lbl.pack(side="right", padx=(8, 0))

        # Content Text Widget with dynamic auto-height & wrapping
        content_text = tk.Text(
            card,
            font=(THEME["font_family"], 10),
            fg=text_color,
            bg=bubble_bg,
            wrap="word",
            relief="flat",
            borderwidth=0,
            highlightthickness=0,
            padx=2,
            pady=2
        )
        content_text.insert("1.0", self.content)
        content_text.config(state="disabled")

        # Auto-size height based on lines
        line_count = int(content_text.index("end-1c").split(".")[0])
        # Approximate wrap height
        char_count = len(self.content)
        calc_height = max(line_count, (char_count // 65) + 1)
        content_text.config(height=min(calc_height, 22), width=min(max(char_count + 5, 25), 72))
        content_text.pack(fill="both", expand=True)

        # Footer Action Bar (Copy button)
        footer_frame = tk.Frame(card, bg=bubble_bg)
        footer_frame.pack(fill="x", pady=(4, 0))

        copy_btn = tk.Label(
            footer_frame,
            text="📋 Copy",
            font=(THEME["font_family"], 8),
            fg="#cbd5e1" if is_user else THEME["text_secondary"],
            bg=bubble_bg,
            cursor="hand2"
        )
        copy_btn.pack(side="right")
        copy_btn.bind("<Button-1>", lambda e: self._copy_text(copy_btn))

    def _copy_text(self, label_widget):
        if self.on_copy:
            self.on_copy(self.content)
        label_widget.config(text="✓ Copied!", fg="#10b981")
        self.after(1500, lambda: label_widget.config(text="📋 Copy", fg=THEME["text_secondary"]))


class NexusApp(tk.Tk):
    """Main Application Window with Modern UI and Asynchronous Worker Engine."""

    def __init__(self):
        super().__init__()

        # Window Setup
        self.title(f"{BOT_NAME} v{BOT_VERSION}")
        self.geometry("1160x780")
        self.minsize(960, 640)
        self.configure(bg=THEME["bg_main"])

        # Engine Init
        self.bot = HybridChatbot()
        self.sound_enabled = True
        self.is_thinking = False
        self.anim_step = 0

        # Build Full UI
        self._setup_styles()
        self._build_layout()

        # Send initial warm welcome
        self.after(300, self._send_initial_welcome)

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        # Scrollbar styling
        style.configure(
            "Vertical.TScrollbar",
            background=THEME["border_color"],
            troughcolor=THEME["bg_chat"],
            arrowcolor=THEME["accent_light"],
            relief="flat",
            borderwidth=0
        )

        # Combobox styling
        style.configure(
            "Dark.TCombobox",
            fieldbackground=THEME["bg_sidebar"],
            background=THEME["border_color"],
            foreground=THEME["text_primary"],
            arrowcolor=THEME["accent_light"],
            bordercolor=THEME["border_color"],
            lightcolor=THEME["border_color"],
            darkcolor=THEME["border_color"]
        )

    def _build_layout(self):
        # Master Grid Configuration
        self.columnconfigure(0, weight=0, minsize=310)  # Sidebar
        self.columnconfigure(1, weight=1)               # Main Chat Area
        self.rowconfigure(0, weight=1)

        # 1. Left Sidebar Inspector
        self._build_sidebar()

        # 2. Main Chat Workspace (Header, Scrollable Canvas, Quick Pills, Input Bar)
        self._build_chat_workspace()

    # =========================================================================
    # SIDEBAR CONTROL CENTER
    # =========================================================================
    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg=THEME["bg_sidebar"], width=310, padx=16, pady=16)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.pack_propagate(False)

        # Brand Logo & Title
        title_box = tk.Frame(sidebar, bg=THEME["bg_sidebar"])
        title_box.pack(fill="x", pady=(0, 14))

        logo_lbl = tk.Label(
            title_box,
            text="⚡ NEXUS AI",
            font=(THEME["font_family"], 16, "bold"),
            fg=THEME["accent_light"],
            bg=THEME["bg_sidebar"]
        )
        logo_lbl.pack(anchor="w")

        tag_lbl = tk.Label(
            title_box,
            text=BOT_TAGLINE,
            font=(THEME["font_family"], 8),
            fg=THEME["text_secondary"],
            bg=THEME["bg_sidebar"]
        )
        tag_lbl.pack(anchor="w")

        # Online Status Indicator
        status_card = tk.Frame(
            sidebar,
            bg="#0f172a",
            highlightbackground=THEME["border_color"],
            highlightthickness=1,
            padx=10,
            pady=8
        )
        status_card.pack(fill="x", pady=(0, 14))

        self.status_dot = tk.Label(
            status_card,
            text="●",
            font=(THEME["font_family"], 11),
            fg=THEME["accent_green"],
            bg="#0f172a"
        )
        self.status_dot.pack(side="left", padx=(0, 6))

        self.status_text = tk.Label(
            status_card,
            text="System Engine: Online (Hybrid)",
            font=(THEME["font_family"], 9, "bold"),
            fg=THEME["text_primary"],
            bg="#0f172a"
        )
        self.status_text.pack(side="left")

        # Mode Selection
        mode_hdr = tk.Label(
            sidebar,
            text="EXECUTION ENGINE MODE",
            font=(THEME["font_family"], 8, "bold"),
            fg=THEME["accent_light"],
            bg=THEME["bg_sidebar"]
        )
        mode_hdr.pack(anchor="w", pady=(4, 4))

        self.mode_var = tk.StringVar(value=HybridChatbot.MODE_HYBRID)
        mode_cb = ttk.Combobox(
            sidebar,
            textvariable=self.mode_var,
            values=[
                HybridChatbot.MODE_HYBRID,
                HybridChatbot.MODE_RULE_ONLY,
                HybridChatbot.MODE_AI_ONLY
            ],
            state="readonly",
            style="Dark.TCombobox",
            font=(THEME["font_family"], 9)
        )
        mode_cb.pack(fill="x", pady=(0, 10))
        mode_cb.bind("<<ComboboxSelected>>", self._on_mode_change)

        # Groq Cloud Model Selection
        model_hdr = tk.Label(
            sidebar,
            text="GROQ CLOUD LLM MODEL",
            font=(THEME["font_family"], 8, "bold"),
            fg=THEME["accent_light"],
            bg=THEME["bg_sidebar"]
        )
        model_hdr.pack(anchor="w", pady=(4, 4))

        self.model_var = tk.StringVar(value=DEFAULT_MODEL)
        model_cb = ttk.Combobox(
            sidebar,
            textvariable=self.model_var,
            values=AVAILABLE_MODELS,
            state="readonly",
            style="Dark.TCombobox",
            font=(THEME["font_family"], 9)
        )
        model_cb.pack(fill="x", pady=(0, 14))
        model_cb.bind("<<ComboboxSelected>>", self._on_model_change)

        # Modular Flow Quick Launchers
        flows_hdr = tk.Label(
            sidebar,
            text="MODULAR FLOW LAUNCHERS",
            font=(THEME["font_family"], 8, "bold"),
            fg=THEME["accent_light"],
            bg=THEME["bg_sidebar"]
        )
        flows_hdr.pack(anchor="w", pady=(0, 6))

        flows_frame = tk.Frame(sidebar, bg=THEME["bg_sidebar"])
        flows_frame.pack(fill="x", pady=(0, 14))

        flows = [
            ("🛠️ Tech Support Wizard", "tech support"),
            ("💳 Billing & Orders", "billing"),
            ("🧠 Interactive Quiz", "quiz"),
            ("⚙️ Telemetry Diagnostics", "diagnostics"),
            ("⭐ Rate & Feedback", "feedback")
        ]

        for label, cmd in flows:
            btn = tk.Button(
                flows_frame,
                text=label,
                font=(THEME["font_family"], 9),
                fg=THEME["text_primary"],
                bg="#334155",
                activebackground=THEME["accent"],
                activeforeground="#ffffff",
                relief="flat",
                anchor="w",
                padx=10,
                pady=4,
                cursor="hand2",
                command=lambda c=cmd: self._send_user_message(c)
            )
            btn.pack(fill="x", pady=2)

        # Live State Inspector Card
        inspector_hdr = tk.Label(
            sidebar,
            text="LIVE SESSION TELEMETRY",
            font=(THEME["font_family"], 8, "bold"),
            fg=THEME["accent_light"],
            bg=THEME["bg_sidebar"]
        )
        inspector_hdr.pack(anchor="w", pady=(0, 4))

        self.inspector_card = tk.Frame(
            sidebar,
            bg="#0f172a",
            highlightbackground=THEME["border_color"],
            highlightthickness=1,
            padx=10,
            pady=8
        )
        self.inspector_card.pack(fill="x", pady=(0, 14))

        self.lbl_intent = tk.Label(self.inspector_card, text="• Intent: Idle", font=(THEME["font_family"], 8), fg=THEME["text_secondary"], bg="#0f172a", anchor="w")
        self.lbl_intent.pack(fill="x")

        self.lbl_confidence = tk.Label(self.inspector_card, text="• Match Confidence: 100%", font=(THEME["font_family"], 8), fg=THEME["text_secondary"], bg="#0f172a", anchor="w")
        self.lbl_confidence.pack(fill="x")

        self.lbl_tree = tk.Label(self.inspector_card, text="• Active Tree: None", font=(THEME["font_family"], 8), fg=THEME["text_secondary"], bg="#0f172a", anchor="w")
        self.lbl_tree.pack(fill="x")

        self.lbl_turns = tk.Label(self.inspector_card, text="• Interaction Turns: 0", font=(THEME["font_family"], 8), fg=THEME["text_secondary"], bg="#0f172a", anchor="w")
        self.lbl_turns.pack(fill="x")

        # Bottom Tools (Export, Clear, Sound)
        bottom_tools = tk.Frame(sidebar, bg=THEME["bg_sidebar"])
        bottom_tools.pack(side="bottom", fill="x")

        btn_export = tk.Button(
            bottom_tools,
            text="💾 Export Chat",
            font=(THEME["font_family"], 8, "bold"),
            fg="#ffffff",
            bg="#059669",
            activebackground="#047857",
            relief="flat",
            padx=8,
            pady=5,
            cursor="hand2",
            command=self._export_dialog
        )
        btn_export.pack(side="left", expand=True, fill="x", padx=(0, 4))

        btn_clear = tk.Button(
            bottom_tools,
            text="🗑️ Reset",
            font=(THEME["font_family"], 8, "bold"),
            fg="#ffffff",
            bg="#dc2626",
            activebackground="#b91c1c",
            relief="flat",
            padx=8,
            pady=5,
            cursor="hand2",
            command=self._clear_conversation
        )
        btn_clear.pack(side="left", expand=True, fill="x", padx=(4, 0))

    # =========================================================================
    # CHAT WORKSPACE
    # =========================================================================
    def _build_chat_workspace(self):
        chat_root = tk.Frame(self, bg=THEME["bg_chat"])
        chat_root.grid(row=0, column=1, sticky="nsew")

        chat_root.rowconfigure(1, weight=1)
        chat_root.columnconfigure(0, weight=1)

        # 1. Top Bar (Search & Mode Badge & Sound Toggle)
        top_bar = tk.Frame(chat_root, bg=THEME["bg_sidebar"], height=52, padx=16, pady=8)
        top_bar.grid(row=0, column=0, sticky="ew")

        top_title = tk.Label(
            top_bar,
            text="💬 Nexus Intelligent Console",
            font=(THEME["font_family"], 11, "bold"),
            fg=THEME["text_primary"],
            bg=THEME["bg_sidebar"]
        )
        top_title.pack(side="left")

        # Sound Toggle
        self.sound_btn = tk.Button(
            top_bar,
            text="🔊 Sound: ON",
            font=(THEME["font_family"], 8),
            fg=THEME["text_primary"],
            bg="#334155",
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2",
            command=self._toggle_sound
        )
        self.sound_btn.pack(side="right", padx=(8, 0))

        # Help / Architecture Cheat Sheet Modal Button
        help_btn = tk.Button(
            top_bar,
            text="❓ Cheat Sheet",
            font=(THEME["font_family"], 8),
            fg=THEME["text_primary"],
            bg="#334155",
            relief="flat",
            padx=8,
            pady=3,
            cursor="hand2",
            command=self._show_cheat_sheet
        )
        help_btn.pack(side="right", padx=(8, 0))

        # Search Bar inside top bar
        search_box = tk.Frame(top_bar, bg="#0f172a", highlightbackground=THEME["border_color"], highlightthickness=1)
        search_box.pack(side="right", padx=10)

        search_icon = tk.Label(search_box, text="🔍", font=(THEME["font_family"], 8), fg=THEME["text_secondary"], bg="#0f172a")
        search_icon.pack(side="left", padx=4)

        self.search_entry = tk.Entry(
            search_box,
            font=(THEME["font_family"], 9),
            fg=THEME["text_primary"],
            bg="#0f172a",
            insertbackground="#ffffff",
            relief="flat",
            width=18
        )
        self.search_entry.pack(side="left", padx=4, pady=2)
        self.search_entry.bind("<KeyRelease>", self._on_search_query)

        # 2. Scrollable Chat Canvas
        canvas_frame = tk.Frame(chat_root, bg=THEME["bg_chat"])
        canvas_frame.grid(row=1, column=0, sticky="nsew")

        self.canvas = tk.Canvas(
            canvas_frame,
            bg=THEME["bg_chat"],
            highlightthickness=0,
            borderwidth=0
        )
        self.scrollbar = ttk.Scrollbar(
            canvas_frame,
            orient="vertical",
            command=self.canvas.yview,
            style="Vertical.TScrollbar"
        )
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.messages_container = tk.Frame(self.canvas, bg=THEME["bg_chat"])
        self.canvas_window = self.canvas.create_window((0, 0), window=self.messages_container, anchor="nw")

        self.messages_container.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Typing Indicator Badge (Hidden by default)
        self.typing_frame = tk.Frame(chat_root, bg=THEME["bg_chat"])
        self.typing_frame.grid(row=2, column=0, sticky="w", padx=24, pady=2)
        self.typing_label = tk.Label(
            self.typing_frame,
            text="🤖 Nexus is thinking ● ● ●",
            font=(THEME["font_family"], 9, "italic"),
            fg=THEME["accent_light"],
            bg=THEME["bg_chat"]
        )

        # 3. Dynamic Quick Action Pills Bar
        self.pills_container = tk.Frame(chat_root, bg=THEME["bg_main"], height=36, padx=16, pady=4)
        self.pills_container.grid(row=3, column=0, sticky="ew")

        # 4. Bottom Input Bar
        input_bar = tk.Frame(chat_root, bg=THEME["bg_sidebar"], padx=16, pady=12)
        input_bar.grid(row=4, column=0, sticky="ew")

        input_wrapper = tk.Frame(
            input_bar,
            bg=THEME["bg_main"],
            highlightbackground=THEME["border_color"],
            highlightthickness=1,
            padx=8,
            pady=4
        )
        input_wrapper.pack(fill="x")

        self.input_entry = tk.Entry(
            input_wrapper,
            font=(THEME["font_family"], 11),
            fg=THEME["text_primary"],
            bg=THEME["bg_main"],
            insertbackground="#ffffff",
            relief="flat"
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(8, 8), pady=4)
        self.input_entry.bind("<Return>", lambda e: self._on_send_click())
        self.input_entry.focus_set()

        self.send_btn = tk.Button(
            input_wrapper,
            text="  Send ➔  ",
            font=(THEME["font_family"], 9, "bold"),
            fg="#ffffff",
            bg=THEME["accent"],
            activebackground=THEME["accent_hover"],
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2",
            command=self._on_send_click
        )
        self.send_btn.pack(side="right")

    # =========================================================================
    # EVENT HANDLERS & ANIMATIONS
    # =========================================================================
    def _play_sound(self, sound_type: str = "send"):
        if not self.sound_enabled or not HAS_WINSOUND:
            return
        try:
            if sound_type == "send":
                winsound.Beep(880, 40)
            elif sound_type == "receive":
                winsound.Beep(1200, 50)
            elif sound_type == "pill":
                winsound.Beep(980, 30)
        except Exception:
            pass

    def _toggle_sound(self):
        self.sound_enabled = not self.sound_enabled
        txt = "🔊 Sound: ON" if self.sound_enabled else "🔇 Sound: OFF"
        self.sound_btn.config(text=txt)

    def _on_mode_change(self, event=None):
        new_mode = self.mode_var.get()
        self.bot.set_mode(new_mode)
        self.status_text.config(text=f"System Engine: {new_mode}")
        self._update_telemetry("mode_switched", 1.0, self.bot.session.get("active_tree"))

    def _on_model_change(self, event=None):
        new_model = self.model_var.get()
        self.bot.set_model(new_model)

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _scroll_to_bottom(self):
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)

    def _animate_typing(self):
        if not self.is_thinking:
            self.typing_label.pack_forget()
            return
        dots = ["● ○ ○", "○ ● ○", "○ ○ ●", "● ● ●"]
        self.anim_step = (self.anim_step + 1) % len(dots)
        self.typing_label.config(text=f"🤖 Nexus is processing {dots[self.anim_step]}")
        self.after(280, self._animate_typing)

    def _set_typing(self, active: bool):
        self.is_thinking = active
        if active:
            self.typing_label.pack(side="left")
            self._animate_typing()
            self.send_btn.config(state="disabled", bg="#475569")
        else:
            self.typing_label.pack_forget()
            self.send_btn.config(state="normal", bg=THEME["accent"])

    # =========================================================================
    # CORE CONVERSATIONAL DISPATCH
    # =========================================================================
    def _send_initial_welcome(self):
        res = self.bot.process_input("hello")
        self._add_message_bubble(
            role="assistant",
            content=res["response"],
            timestamp=res["timestamp"],
            source=res["source"]
        )
        self._render_quick_pills(res.get("quick_replies", []))
        self._update_telemetry(res["intent"], res["confidence"], None)

    def _on_send_click(self):
        text = self.input_entry.get().strip()
        if not text or self.is_thinking:
            return
        self.input_entry.delete(0, "end")
        self._send_user_message(text)

    def _send_user_message(self, text: str):
        if self.is_thinking:
            return

        self._play_sound("send")
        curr_time = time.strftime("%H:%M:%S")

        # 1. Render User Bubble
        self._add_message_bubble(role="user", content=text, timestamp=curr_time)
        self._scroll_to_bottom()

        # 2. Start Typing Animation & Worker Thread
        self._set_typing(True)

        threading.Thread(
            target=self._async_worker,
            args=(text,),
            daemon=True
        ).start()

    def _async_worker(self, text: str):
        """Processes query asynchronously so GUI stays completely fluid."""
        start_t = time.time()
        result = self.bot.process_input(text)
        elapsed = round(time.time() - start_t, 2)

        # Dispatch UI update to main Tkinter loop
        self.after(0, lambda: self._on_response_ready(result, elapsed))

    def _on_response_ready(self, result: Dict[str, Any], latency: float):
        self._set_typing(False)
        self._play_sound("receive")

        # Render Bot Bubble
        self._add_message_bubble(
            role="assistant",
            content=result["response"],
            timestamp=result["timestamp"],
            source=result["source"]
        )

        # Update Pills & Telemetry
        self._render_quick_pills(result.get("quick_replies", []))
        self._update_telemetry(
            intent=result.get("intent", "general"),
            confidence=result.get("confidence", 1.0),
            active_tree=self.bot.session.get("active_tree"),
            latency=latency
        )
        self._scroll_to_bottom()

    def _add_message_bubble(self, role: str, content: str, timestamp: str, source: str = "Rule Engine"):
        bubble = ModernChatBubble(
            self.messages_container,
            role=role,
            content=content,
            timestamp=timestamp,
            source=source,
            on_copy=self._copy_to_clipboard
        )
        bubble.pack(fill="x", expand=True)
        self._scroll_to_bottom()

    def _render_quick_pills(self, pills: list):
        for widget in self.pills_container.winfo_children():
            widget.destroy()

        if not pills:
            return

        lbl = tk.Label(
            self.pills_container,
            text="⚡ Suggestions:",
            font=(THEME["font_family"], 8, "bold"),
            fg=THEME["accent_light"],
            bg=THEME["bg_main"]
        )
        lbl.pack(side="left", padx=(0, 6))

        for p in pills[:5]:
            p_btn = tk.Button(
                self.pills_container,
                text=p,
                font=(THEME["font_family"], 8),
                fg=THEME["text_primary"],
                bg="#334155",
                activebackground=THEME["accent"],
                activeforeground="#ffffff",
                relief="flat",
                padx=8,
                pady=2,
                cursor="hand2",
                command=lambda val=p: self._on_pill_clicked(val)
            )
            p_btn.pack(side="left", padx=3)

    def _on_pill_clicked(self, pill_text: str):
        self._play_sound("pill")
        self._send_user_message(pill_text)

    def _update_telemetry(self, intent: str, confidence: float, active_tree: str, latency: float = 0.0):
        self.lbl_intent.config(text=f"• Intent: {intent.upper()}")
        self.lbl_confidence.config(text=f"• Confidence: {int(confidence * 100)}%")
        tree_txt = active_tree.replace('_', ' ').title() if active_tree else "None (Main Router)"
        self.lbl_tree.config(text=f"• Tree: {tree_txt}")
        turns = len(self.bot.history) // 2
        self.lbl_turns.config(text=f"• Interaction Turns: {turns}")

    # =========================================================================
    # SEARCH & UTILITY FEATURES
    # =========================================================================
    def _on_search_query(self, event=None):
        query = self.search_entry.get().strip().lower()
        # Highlights bubbles matching query
        for child in self.messages_container.winfo_children():
            if isinstance(child, ModernChatBubble):
                if not query or query in child.content.lower():
                    child.pack(fill="x", expand=True)
                else:
                    child.pack_forget()

    def _copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)

    def _export_dialog(self):
        fmt = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown Document", "*.md"), ("JSON Data", "*.json"), ("Plain Text", "*.txt")],
            title="Export Conversation History"
        )
        if fmt:
            ext = os.path.splitext(fmt)[1].replace(".", "")
            content = self.bot.export_history(ext)
            with open(fmt, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("Export Successful", f"Chat history exported to:\n{fmt}")

    def _clear_conversation(self):
        if messagebox.askyesno("Reset Conversation", "Are you sure you want to clear the chat and reset session state?"):
            self.bot.reset_session()
            for widget in self.messages_container.winfo_children():
                widget.destroy()
            self._send_initial_welcome()

    def _show_cheat_sheet(self):
        modal = tk.Toplevel(self)
        modal.title("Nexus AI - Architecture & Flow Cheat Sheet")
        modal.geometry("640x520")
        modal.configure(bg=THEME["bg_sidebar"])

        txt = tk.Text(
            modal,
            font=(THEME["font_mono"], 9),
            fg=THEME["text_primary"],
            bg="#0f172a",
            padx=14,
            pady=14,
            wrap="word",
            relief="flat"
        )
        txt.pack(fill="both", expand=True, padx=12, pady=12)

        info = f"""================================================================
  NEXUS HYBRID ARCHITECTURE MANUAL & STATE SPECIFICATION
================================================================

1. NLP NORMALIZATION PIPELINE (nlp_normalizer.py)
   • Contraction expansion (e.g. "can't" -> "cannot")
   • Punctuation cleaning & whitespace collapse
   • Regex entity extractors (Order IDs #ORD-xxxx, Emails, Currency amounts)
   • Jaccard similarity & keyword intent scoring

2. NESTED STATE LOGIC & HELP TREES (dialogue_trees.py)
   • Technical Support Tree:
     - Step 0: Category Menu (WiFi, Performance, Software, Hardware)
     - Step 1: Specific troubleshooting guides
     - Step 2: Resolution verification
     - Step 3: Senior engineering ticket creation
   • Billing & Orders Tree:
     - Order tracking (#ORD-xxxx)
     - Automated refund calculator with 3% fee deduction
     - Secure PDF invoice email dispatcher
   • Interactive Tech Knowledge Quiz:
     - Stateful 3-question evaluation with live scoring
   • Diagnostics & Telemetry:
     - Real-time engine health, OS specs, runtime version
   • User Experience Review:
     - 1-5 Star sentiment recorder

3. GROQ CLOUD NEURAL BRAIN (groq_engine.py)
   • High-speed inference with Groq Cloud LLM
   • Clean <think> tag stripper
   • Automatic graceful offline/fallback handling

4. OPERATING MODES
   • Smart Hybrid: Rules execute structured flows; Groq AI handles open queries.
   • Pure Rule-Based: Strict deterministic dispatch with fallback tips.
   • Pure Groq AI: Direct LLM completion for all prompts.
================================================================
"""
        txt.insert("1.0", info)
        txt.config(state="disabled")


def launch_gui():
    app = NexusApp()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
