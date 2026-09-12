"""
Main Entry Point for Nexus Hybrid AI Chatbot.
Usage:
    python main.py        -> Launches the Ultra-Modern Tkinter GUI
    python main.py --cli  -> Launches the Rich Terminal CLI Loop
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

def main():
    if "--cli" in sys.argv or "-c" in sys.argv:
        from cli_chatbot import run_cli
        run_cli()
    else:
        from gui_app import launch_gui
        launch_gui()

if __name__ == "__main__":
    main()
