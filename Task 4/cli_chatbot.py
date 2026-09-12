"""
Terminal-Driven Conversational Application Loop.
Fulfills Task 4 terminal bot specifications with modular flows,
NLP text normalization, nested state handlers, and Groq AI fallback.
"""

import os
import sys
import time
from hybrid_chatbot import HybridChatbot
from config import BOT_NAME, BOT_VERSION, AVAILABLE_MODELS

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ANSI Colors for Rich Terminal Interface
class TermColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    BG_DARK = '\033[40m'


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def print_banner():
    banner = f"""{TermColors.CYAN}{TermColors.BOLD}
  +=====================================================================+
  |    * {BOT_NAME} - Terminal Agent v{BOT_VERSION} *                   |
  |    Multi-Intent Rule Engine + Groq Cloud Neural Brain               |
  +=====================================================================+{TermColors.ENDC}
"""
    print(banner)


def print_help_menu():
    print(f"""{TermColors.HEADER}{TermColors.BOLD}
  [TERMINAL COMMANDS & SHORTCUTS]{TermColors.ENDC}
  • {TermColors.GREEN}/help{TermColors.ENDC}    : Display this command manual
  • {TermColors.GREEN}/mode{TermColors.ENDC}    : Toggle (1: Hybrid | 2: Pure Rules | 3: Pure AI)
  • {TermColors.GREEN}/model{TermColors.ENDC}   : Switch Groq LLM model
  • {TermColors.GREEN}/state{TermColors.ENDC}   : Inspect active session variables & tree state
  • {TermColors.GREEN}/export{TermColors.ENDC}  : Save conversation transcript to file
  • {TermColors.GREEN}/clear{TermColors.ENDC}   : Clear terminal and reset session
  • {TermColors.GREEN}/exit{TermColors.ENDC}    : Exit application loop

  {TermColors.HEADER}[MODULAR HELPTREES & FLOWS]{TermColors.ENDC}
  • Type '{TermColors.CYAN}tech support{TermColors.ENDC}' : Launch Technical Troubleshooting Wizard
  • Type '{TermColors.CYAN}billing{TermColors.ENDC}'      : Access Orders, Invoices & Refund Center
  • Type '{TermColors.CYAN}quiz{TermColors.ENDC}'         : Start Interactive Tech Knowledge Quiz
  • Type '{TermColors.CYAN}diagnostics{TermColors.ENDC}'  : View system telemetry & uptime
  • Type '{TermColors.CYAN}feedback{TermColors.ENDC}'     : Rate bot and submit review
  • Or type any open-ended question to engage the Groq AI Brain!
""")


def run_cli():
    # Enable ANSI escape sequences on Windows 10/11
    if os.name == 'nt':
        os.system('color')

    clear_terminal()
    print_banner()
    bot = HybridChatbot()

    print(f"{TermColors.GREEN}✓ System initialized.{TermColors.ENDC} Mode: {TermColors.CYAN}{bot.mode}{TermColors.ENDC}")
    print(f"Type {TermColors.BOLD}'/help'{TermColors.ENDC} for commands or start chatting below.\n")

    # Initial greeting from rule engine
    init_res = bot.process_input("hello")
    print(f"{TermColors.CYAN}{TermColors.BOLD}[Nexus AI]:{TermColors.ENDC} {init_res['response']}\n")

    while True:
        try:
            user_input = input(f"{TermColors.BLUE}{TermColors.BOLD}[User] >> {TermColors.ENDC}").strip()
            if not user_input:
                continue

            # Command Handling
            if user_input.lower() in ["/exit", "exit", "/quit", "quit"]:
                print(f"\n{TermColors.GREEN}Thank you for using {BOT_NAME}. Goodbye!{TermColors.ENDC}")
                break

            elif user_input.lower() == "/help":
                print_help_menu()
                continue

            elif user_input.lower() == "/clear":
                clear_terminal()
                print_banner()
                bot.reset_session()
                print(f"{TermColors.GREEN}✓ Conversation reset and terminal cleared.{TermColors.ENDC}\n")
                continue

            elif user_input.lower() == "/state":
                print(f"\n{TermColors.HEADER}--- [ACTIVE SESSION STATE INSPECTOR] ---{TermColors.ENDC}")
                for k, v in bot.session.items():
                    print(f"  • {TermColors.BOLD}{k}:{TermColors.ENDC} {v}")
                print(f"{TermColors.HEADER}----------------------------------------{TermColors.ENDC}\n")
                continue

            elif user_input.lower() == "/mode":
                print(f"\n{TermColors.HEADER}Select Execution Mode:{TermColors.ENDC}")
                print(f"  1) {HybridChatbot.MODE_HYBRID}")
                print(f"  2) {HybridChatbot.MODE_RULE_ONLY}")
                print(f"  3) {HybridChatbot.MODE_AI_ONLY}")
                sel = input(f"{TermColors.YELLOW}Choose (1-3): {TermColors.ENDC}").strip()
                if sel == "1":
                    bot.set_mode(HybridChatbot.MODE_HYBRID)
                elif sel == "2":
                    bot.set_mode(HybridChatbot.MODE_RULE_ONLY)
                elif sel == "3":
                    bot.set_mode(HybridChatbot.MODE_AI_ONLY)
                print(f"{TermColors.GREEN}✓ Mode updated to: {bot.mode}{TermColors.ENDC}\n")
                continue

            elif user_input.lower() == "/model":
                print(f"\n{TermColors.HEADER}Available Groq Cloud Models:{TermColors.ENDC}")
                for i, m in enumerate(AVAILABLE_MODELS, 1):
                    print(f"  {i}) {m}")
                sel = input(f"{TermColors.YELLOW}Choose model (1-{len(AVAILABLE_MODELS)}): {TermColors.ENDC}").strip()
                if sel.isdigit() and 1 <= int(sel) <= len(AVAILABLE_MODELS):
                    chosen = AVAILABLE_MODELS[int(sel) - 1]
                    bot.set_model(chosen)
                    print(f"{TermColors.GREEN}✓ Active model set to: {chosen}{TermColors.ENDC}\n")
                continue

            elif user_input.lower() == "/export":
                transcript = bot.export_history("markdown")
                filename = f"chat_export_{int(time.time())}.md"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(transcript)
                print(f"{TermColors.GREEN}✓ Export saved successfully to: {os.path.abspath(filename)}{TermColors.ENDC}\n")
                continue

            # Process Conversational Query
            print(f"{TermColors.WARNING}⚡ Processing...{TermColors.ENDC}", end="\r")
            result = bot.process_input(user_input)
            print(" " * 30, end="\r")  # Clear processing line

            # Badge formatting
            source_badge = f"{TermColors.GREEN}[{result['source']}]{TermColors.ENDC}"
            intent_badge = f"{TermColors.HEADER}[Intent: {result['intent']} | Conf: {result['confidence']*100:.0f}%]{TermColors.ENDC}"

            print(f"{TermColors.CYAN}{TermColors.BOLD}[Nexus AI]{TermColors.ENDC} {source_badge} {intent_badge}:")
            print(f"{result['response']}\n")

            if result.get("quick_replies"):
                pills_str = " | ".join([f"[{p}]" for p in result["quick_replies"]])
                print(f"{TermColors.WARNING}💡 Quick Suggestions:{TermColors.ENDC} {pills_str}\n")

        except KeyboardInterrupt:
            print(f"\n\n{TermColors.WARNING}Session interrupted. Exiting...{TermColors.ENDC}")
            break
        except Exception as e:
            print(f"\n{TermColors.FAIL}⚠️ Error in processing loop: {str(e)}{TermColors.ENDC}\n")


if __name__ == "__main__":
    run_cli()
