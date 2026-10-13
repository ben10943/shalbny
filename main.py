"""
Main Entry Point for Shalbny.
Usage:
    python main.py              # Starts in background with System Tray icon
    python main.py --settings   # Starts and immediately shows settings window
"""
import sys
from pathlib import Path

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.app import ShalbnyApp


def main():
    show_settings = "--settings" in sys.argv or "-s" in sys.argv
    app = ShalbnyApp()
    app.run(show_settings_on_start=show_settings)


if __name__ == "__main__":
    main()
