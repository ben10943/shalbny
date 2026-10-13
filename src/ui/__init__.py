"""
UI module for Shalbny.
"""
from .assets import create_app_icon
from .settings_window import SettingsWindow
from .tray import TrayIconManager

__all__ = ["create_app_icon", "SettingsWindow", "TrayIconManager"]
