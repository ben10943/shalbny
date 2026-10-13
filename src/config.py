"""
Configuration manager for Shalbny.
Handles saving/loading settings from JSON and managing Windows startup registry.
"""
import os
import sys
import json
import winreg
from pathlib import Path
from typing import Any, Dict

CONFIG_DIR = Path.home() / ".shalbny"
CONFIG_FILE = CONFIG_DIR / "config.json"
REG_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "Shalbny"

DEFAULT_CONFIG: Dict[str, Any] = {
    "hotkey": "alt+s",
    "app_language": "ar",
    "conversion_count": 0,
    "switch_system_language": True,
    "play_sound": True,
    "sound_theme": "soft_pop",
    "restore_clipboard": True,
    "active_profile": "ar_en",
    "autostart": False,
    "developer_name": "KHALED ABDELMONEM",
    "developer_phone": "01015362991",
    "developer_github": "https://github.com/ben10943",
    "developer_linkedin": "https://www.linkedin.com/in/khaled-moneam",
    "developer_role": "Lead Software Engineer & System Architect"
}


class ConfigManager:
    """Manages application settings and persistence."""

    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.config: Dict[str, Any] = DEFAULT_CONFIG.copy()
        self.load()

    def load(self) -> None:
        """Load settings from JSON file."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.config.update(saved)
            except Exception:
                pass

    def save(self) -> None:
        """Save settings to JSON file."""
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self.config[key] = value
        self.save()

    def increment_conversion_count(self) -> int:
        """Increments conversion rescue counter and saves config."""
        count = int(self.config.get("conversion_count", 0)) + 1
        self.config["conversion_count"] = count
        self.save()
        return count

    def reset_defaults(self) -> None:
        """Resets all configuration values back to official factory defaults."""
        self.config = DEFAULT_CONFIG.copy()
        self.save()

    def set_autostart(self, enable: bool) -> bool:
        """Configures Windows registry to launch Shalbny on user login."""
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
                if enable:
                    # If running as script, use pythonw with main script
                    if getattr(sys, "frozen", False):
                        cmd = f'"{sys.executable}"'
                    else:
                        main_script = (Path(__file__).parent.parent / "main.py").resolve()
                        python_exe = sys.executable.replace("python.exe", "pythonw.exe")
                        cmd = f'"{python_exe}" "{main_script}"'

                    winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
                else:
                    try:
                        winreg.DeleteValue(key, APP_NAME)
                    except FileNotFoundError:
                        pass
            self.set("autostart", enable)
            return True
        except Exception:
            return False
