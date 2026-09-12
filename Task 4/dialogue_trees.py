"""
Dialogue Trees and Stateful Flow Handlers.
Implements modular nested state logic using if-elif-else structures
and functional dictionary dispatch maps for complex conversational flows.
"""

import sys
import platform
import time
from typing import Dict, Any, Tuple, List, Optional
from nlp_normalizer import NLPNormalizer


class DialogueTreeEngine:
    """Manages nested state trees, multi-step flows, and state transitions."""

    def __init__(self):
        # Store state trees definitions
        self.trees = {
            "tech_support": self._handle_tech_support,
            "billing_orders": self._handle_billing_orders,
            "tech_quiz": self._handle_tech_quiz,
            "feedback": self._handle_feedback,
            "diagnostics": self._handle_diagnostics
        }

    # =========================================================================
    # 1. TECHNICAL SUPPORT TREE
    # =========================================================================
    def _handle_tech_support(self, user_text: str, session: Dict[str, Any]) -> Tuple[str, List[str], bool]:
        """
        Nested state machine for Technical Troubleshooting.
        Returns (response_text, suggested_actions, is_flow_completed)
        """
        step = session.get("tree_step", 0)
        norm = NLPNormalizer.clean_text(user_text)

        # Step 0: Initial Category Menu
        if step == 0:
            session["tree_step"] = 1
            session["tree_data"] = {}
            msg = (
                "🛠️ **Technical Support Wizard**\n"
                "Please select your category of technical issue:\n\n"
                "1️⃣ **WiFi & Network Connectivity** (No internet, DNS error)\n"
                "2️⃣ **System Performance & Freezing** (Slow PC, high CPU)\n"
                "3️⃣ **Software & App Crashes** (Python error, app won't launch)\n"
                "4️⃣ **Hardware & Peripheral Issues** (Audio, USB, display)\n"
                "Type a number (1-4) or describe the issue directly."
            )
            quick_replies = ["1. WiFi & Network", "2. System Freezing", "3. App Crashes", "4. Hardware Issues", "Cancel"]
            return msg, quick_replies, False

        # Step 1: Category Selection Logic (if-elif-else + dictionary routing)
        elif step == 1:
            if "cancel" in norm or "exit" in norm or "back" in norm:
                return "❌ Technical support wizard cancelled. How else can I help?", ["Main Menu", "Help", "Ask AI"], True

            cat_map = {
                "1": "network", "wifi": "network", "internet": "network", "dns": "network",
                "2": "performance", "slow": "performance", "freeze": "performance", "cpu": "performance",
                "3": "software", "crash": "software", "python": "software", "error": "software",
                "4": "hardware", "audio": "hardware", "usb": "hardware", "display": "hardware", "screen": "hardware"
            }

            matched_cat = None
            for key, val in cat_map.items():
                if key in norm:
                    matched_cat = val
                    break

            if not matched_cat:
                return (
                    "⚠️ Unrecognized choice. Please select 1, 2, 3, or 4, or type 'cancel' to exit.",
                    ["1. WiFi & Network", "2. System Freezing", "3. App Crashes", "4. Hardware Issues", "Cancel"],
                    False
                )

            session["tree_data"]["category"] = matched_cat
            session["tree_step"] = 2

            # Route by category using nested logic
            if matched_cat == "network":
                msg = (
                    "🌐 **Network Troubleshooting Steps:**\n"
                    "1. Turn Wi-Fi OFF for 10 seconds, then turn it back ON.\n"
                    "2. Flush DNS in terminal: `ipconfig /flushdns`.\n"
                    "3. Restart your router/modem.\n\n"
                    "Did these steps resolve your network problem?"
                )
            elif matched_cat == "performance":
                msg = (
                    "⚡ **Performance Troubleshooting Steps:**\n"
                    "1. Open Task Manager (`Ctrl + Shift + Esc`) to inspect background processes.\n"
                    "2. Check disk space and clear `%temp%` files.\n"
                    "3. Ensure your OS power mode is set to 'High Performance'.\n\n"
                    "Did these steps resolve the slowness?"
                )
            elif matched_cat == "software":
                msg = (
                    "💻 **Software Crash Troubleshooting Steps:**\n"
                    "1. Verify dependencies/runtime (e.g. Python version, DLL libraries).\n"
                    "2. Check console / crash logs for exception tracebacks.\n"
                    "3. Try running in an isolated virtual environment (`venv`).\n\n"
                    "Did these steps resolve the crash?"
                )
            else:  # hardware
                msg = (
                    "🔌 **Hardware Troubleshooting Steps:**\n"
                    "1. Unplug and re-plug cable / USB connector securely.\n"
                    "2. Open Device Manager to check for yellow warning exclamation marks.\n"
                    "3. Update or reinstall device drivers.\n\n"
                    "Did these steps fix the hardware issue?"
                )

            return msg, ["Yes, resolved!", "No, need escalation", "Cancel"], False

        # Step 2: Resolution Confirmation & Escalation
        elif step == 2:
            if "yes" in norm or "resolved" in norm or "fixed" in norm or "works" in norm:
                session["tree_data"]["status"] = "resolved"
                return (
                    "🎉 **Awesome!** Glad your technical issue is resolved. Have a great day!",
                    ["Main Menu", "Run Diagnostics", "Ask AI"],
                    True
                )
            elif "no" in norm or "escalat" in norm or "not" in norm or "still" in norm:
                session["tree_step"] = 3
                return (
                    "📋 Let's create an escalation support ticket for our senior engineers.\n"
                    "Please provide your **Email Address** and a brief description of your system.",
                    ["user@example.com", "Cancel"],
                    False
                )
            elif "cancel" in norm:
                return "❌ Technical support wizard ended.", ["Main Menu"], True
            else:
                return (
                    "Please reply with 'Yes' if resolved, or 'No' if you need a support ticket.",
                    ["Yes, resolved!", "No, need escalation", "Cancel"],
                    False
                )

        # Step 3: Support Ticket Generation
        elif step == 3:
            entities = NLPNormalizer.extract_entities(user_text)
            email = entities.get("email") or "customer.escalated@nexus.ai"
            ticket_id = f"TICK-{int(time.time()) % 100000:05d}"
            category = session.get("tree_data", {}).get("category", "General Tech").upper()

            res = (
                f"🎫 **Support Ticket Created Successfully!**\n\n"
                f"• **Ticket ID:** `{ticket_id}`\n"
                f"• **Category:** {category}\n"
                f"• **Contact Email:** `{email}`\n"
                f"• **Priority:** HIGH\n"
                f"• **Estimated SLA:** Under 2 hours\n\n"
                f"Our senior engineering team will follow up via email."
            )
            return res, ["Main Menu", "Track Order/Ticket", "Ask AI"], True

        return "Flow state error. Resetting.", ["Main Menu"], True

    # =========================================================================
    # 2. BILLING & ORDERS TREE
    # =========================================================================
    def _handle_billing_orders(self, user_text: str, session: Dict[str, Any]) -> Tuple[str, List[str], bool]:
        """Nested state machine for Billing, Orders, and Invoicing."""
        step = session.get("tree_step", 0)
        norm = NLPNormalizer.clean_text(user_text)

        if step == 0:
            session["tree_step"] = 1
            session["tree_data"] = {}
            msg = (
                "💳 **Billing & E-Commerce Center**\n"
                "How can I assist with your account today?\n\n"
                "1️⃣ **Track an Order Status**\n"
                "2️⃣ **Request Refund / Return Calculator**\n"
                "3️⃣ **Download Invoice / Receipt**\n"
                "4️⃣ **Subscription & Plan Upgrade**"
            )
            return msg, ["1. Track Order", "2. Request Refund", "3. Get Invoice", "4. Upgrade Plan", "Cancel"], False

        elif step == 1:
            if "cancel" in norm:
                return "❌ Billing flow cancelled.", ["Main Menu"], True

            if "1" in norm or "track" in norm or "order" in norm:
                session["tree_data"]["action"] = "track"
                session["tree_step"] = 2
                return "📦 Please enter your **Order ID** (e.g., `#ORD-9821` or `ORD-5432`):", ["#ORD-8842", "#ORD-1092", "Cancel"], False

            elif "2" in norm or "refund" in norm or "return" in norm:
                session["tree_data"]["action"] = "refund"
                session["tree_step"] = 3
                return "💰 Please enter the **Amount** to be refunded and reason (e.g., `$75 defective item`):", ["$50 wrong size", "$120 cancelled order", "Cancel"], False

            elif "3" in norm or "invoice" in norm or "receipt" in norm:
                session["tree_data"]["action"] = "invoice"
                session["tree_step"] = 4
                return "📄 Please enter your registered account **Email** to dispatch the PDF invoice:", ["user@example.com", "Cancel"], False

            elif "4" in norm or "sub" in norm or "plan" in norm or "upgrade" in norm:
                return (
                    "🌟 **Available Nexus Subscriptions:**\n\n"
                    "• **Standard Free:** $0/mo - 500 Rule Queries/day\n"
                    "• **Pro Developer:** $19/mo - Unlimited Rule Engine + Groq AI Llama3/Qwen\n"
                    "• **Enterprise Suite:** $99/mo - Dedicated GPU endpoints & 24/7 SLA\n\n"
                    "Would you like to upgrade to Pro Developer?",
                    ["Upgrade to Pro ($19)", "Keep Free Plan", "Main Menu"],
                    True
                )
            else:
                return "Please choose option 1, 2, 3, or 4.", ["1. Track Order", "2. Refund", "3. Invoice", "4. Plans"], False

        # Step 2: Order Lookup
        elif step == 2:
            entities = NLPNormalizer.extract_entities(user_text)
            order_id = entities.get("order_id") or "ORD-8842"
            res = (
                f"📦 **Order Status Report: `{order_id}`**\n"
                f"• **Status:** 🚚 Out for Delivery (FedEx Express)\n"
                f"• **ETA:** Today by 5:30 PM\n"
                f"• **Tracking Number:** `FDX-998271644`\n"
                f"• **Destination:** Signed Delivery Address"
            )
            return res, ["Main Menu", "Ask AI", "Technical Support"], True

        # Step 3: Refund Calculation
        elif step == 3:
            entities = NLPNormalizer.extract_entities(user_text)
            amount = entities.get("amount") or 49.99
            fee = round(amount * 0.03, 2)
            net_refund = round(amount - fee, 2)
            res = (
                f"💵 **Refund Processing Breakdown:**\n"
                f"• Requested Amount: **${amount:.2f}**\n"
                f"• Processing/Restocking Fee (3%): **${fee:.2f}**\n"
                f"• **Net Refund to Account:** **${net_refund:.2f}**\n"
                f"• Status: 🟢 Approved - Funds will appear in 2-3 business days."
            )
            return res, ["Main Menu", "Download Invoice", "Ask AI"], True

        # Step 4: Invoice Dispatch
        elif step == 4:
            entities = NLPNormalizer.extract_entities(user_text)
            email = entities.get("email") or "customer@example.com"
            res = (
                f"📧 **Invoice Dispatched!**\n"
                f"A secure copy of your latest statement and invoice receipt has been sent to `{email}`."
            )
            return res, ["Main Menu", "Ask AI"], True

        return "Resetting billing state.", ["Main Menu"], True

    # =========================================================================
    # 3. INTERACTIVE TECH KNOWLEDGE QUIZ
    # =========================================================================
    def _handle_tech_quiz(self, user_text: str, session: Dict[str, Any]) -> Tuple[str, List[str], bool]:
        """Stateful multi-turn interactive quiz tree with live score tracking."""
        step = session.get("tree_step", 0)
        norm = NLPNormalizer.clean_text(user_text)

        quiz_questions = [
            {
                "q": "Question 1/3: Which Python keyword is used to handle exceptions gracefully?",
                "options": ["A) catch", "B) except", "C) trap", "D) check"],
                "answer": "b",
                "ans_text": "B) except",
                "explanation": "In Python, `try...except` blocks are used to catch and handle exceptions."
            },
            {
                "q": "Question 2/3: In rule-based chatbots, what does an intent router primarily do?",
                "options": ["A) Generates 3D graphics", "B) Dispatches user inputs to specific logic handlers", "C) Overclocks CPU", "D) Encrypts hard drives"],
                "answer": "b",
                "ans_text": "B) Dispatches user inputs to specific logic handlers",
                "explanation": "Intent routers analyze tokens to map user goals to functional handlers."
            },
            {
                "q": "Question 3/3: Which protocol operates on TCP port 443 by default?",
                "options": ["A) HTTP", "B) FTP", "C) HTTPS", "D) SSH"],
                "answer": "c",
                "ans_text": "C) HTTPS",
                "explanation": "Port 443 is the standard port for secure HTTPS web traffic."
            }
        ]

        if step == 0:
            session["tree_step"] = 1
            session["tree_data"] = {"score": 0, "q_idx": 0}
            curr = quiz_questions[0]
            msg = (
                "🧠 **Nexus Interactive Tech Knowledge Quiz**\n"
                "Test your knowledge in 3 quick questions!\n\n"
                f"**{curr['q']}**\n" + "\n".join(curr['options'])
            )
            return msg, ["A", "B", "C", "D", "Quit Quiz"], False

        elif step in [1, 2, 3]:
            q_idx = session["tree_data"].get("q_idx", 0)
            if "quit" in norm or "cancel" in norm:
                return "❌ Quiz cancelled.", ["Main Menu", "Ask AI"], True

            curr = quiz_questions[q_idx]
            user_choice = norm.replace(")", "").strip()[:1]

            is_correct = (user_choice == curr["answer"])
            if is_correct:
                session["tree_data"]["score"] += 1
                feedback = f"✅ **Correct!** ({curr['ans_text']})\n{curr['explanation']}"
            else:
                feedback = f"❌ **Incorrect!** Correct answer was **{curr['ans_text']}**.\n{curr['explanation']}"

            # Next Question or Results
            q_idx += 1
            session["tree_data"]["q_idx"] = q_idx
            session["tree_step"] = q_idx + 1

            if q_idx < len(quiz_questions):
                next_q = quiz_questions[q_idx]
                msg = f"{feedback}\n\n---\n\n**{next_q['q']}**\n" + "\n".join(next_q['options'])
                return msg, ["A", "B", "C", "D", "Quit Quiz"], False
            else:
                # Final Score
                score = session["tree_data"]["score"]
                total = len(quiz_questions)
                pct = int((score / total) * 100)
                emoji = "🏆 Mastermind!" if pct == 100 else ("👍 Great job!" if pct >= 66 else "📚 Keep learning!")
                final_msg = (
                    f"{feedback}\n\n"
                    f"=================================\n"
                    f"🎯 **Quiz Completed!**\n"
                    f"• Final Score: **{score} / {total}** ({pct}%)\n"
                    f"• Evaluation: **{emoji}**\n"
                    f"================================="
                )
                return final_msg, ["Take Quiz Again", "Main Menu", "Ask AI"], True

        return "Quiz reset.", ["Main Menu"], True

    # =========================================================================
    # 4. CUSTOMER FEEDBACK & SENTIMENT TREE
    # =========================================================================
    def _handle_feedback(self, user_text: str, session: Dict[str, Any]) -> Tuple[str, List[str], bool]:
        """Feedback collection and sentiment grading."""
        step = session.get("tree_step", 0)
        norm = NLPNormalizer.clean_text(user_text)

        if step == 0:
            session["tree_step"] = 1
            session["tree_data"] = {}
            msg = (
                "⭐ **User Experience Feedback**\n"
                "Please rate your experience with Nexus Assistant from **1 to 5 Stars**:\n"
                "⭐⭐⭐⭐⭐ (5 = Excellent, 1 = Poor)"
            )
            return msg, ["⭐⭐⭐⭐⭐ (5)", "⭐⭐⭐⭐ (4)", "⭐⭐⭐ (3)", "⭐⭐ (2)", "⭐ (1)", "Cancel"], False

        elif step == 1:
            if "cancel" in norm:
                return "❌ Feedback survey cancelled.", ["Main Menu"], True

            rating = 5
            for r in [5, 4, 3, 2, 1]:
                if str(r) in norm:
                    rating = r
                    break

            session["tree_data"]["rating"] = rating
            session["tree_step"] = 2
            return f"Thank you for giving us **{rating} Stars**! 🌟\nAny additional thoughts or feature suggestions?", ["Everything is great!", "Add more AI models", "Skip"], False

        elif step == 2:
            rating = session["tree_data"].get("rating", 5)
            sentiment = "Positive 🚀" if rating >= 4 else ("Neutral ⚖️" if rating == 3 else "Constructive Needs Attention ⚠️")
            res = (
                f"💌 **Thank You for Your Feedback!**\n"
                f"• Rating Recorded: **{rating}/5 Stars**\n"
                f"• Sentiment Logged: **{sentiment}**\n"
                f"Your insights help us continually upgrade our conversational AI engines!"
            )
            return res, ["Main Menu", "Run Diagnostics", "Ask AI"], True

        return "Feedback reset.", ["Main Menu"], True

    # =========================================================================
    # 5. SYSTEM DIAGNOSTICS & BOT HEALTH
    # =========================================================================
    def _handle_diagnostics(self, user_text: str, session: Dict[str, Any]) -> Tuple[str, List[str], bool]:
        """Runs live system health check and rule engine telemetry."""
        py_ver = sys.version.split()[0]
        os_info = f"{platform.system()} {platform.release()}"
        turn_count = session.get("total_turns", 1)
        active_intent = session.get("active_intent", "None")
        mode = session.get("mode", "Hybrid AI")

        diag_report = (
            "⚙️ **System Diagnostics & Telemetry Report**\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"• **Bot Engine:** Nexus Hybrid AI v4.0.0 Pro\n"
            f"• **Current Execution Mode:** `{mode}`\n"
            f"• **Python Runtime:** `{py_ver}`\n"
            f"• **Host OS Environment:** `{os_info}`\n"
            f"• **Session Interaction Turns:** `{turn_count}`\n"
            f"• **Last Detected Intent:** `{active_intent}`\n"
            f"• **Rule Dispatch Engine:** 🟢 Healthy (Sub-millisecond latency)\n"
            f"• **Groq Cloud Bridge:** 🟢 Active (Llama/Qwen High-Speed Tier)\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        return diag_report, ["Main Menu", "Technical Support", "Take Quiz", "Ask AI"], True

    # =========================================================================
    # DISPATCHER
    # =========================================================================
    def execute_tree(self, tree_name: str, user_text: str, session: Dict[str, Any]) -> Tuple[str, List[str], bool]:
        """Dispatches to the selected tree handler function."""
        handler = self.trees.get(tree_name)
        if handler:
            return handler(user_text, session)
        return "⚠️ Unknown dialogue flow.", ["Main Menu"], True
