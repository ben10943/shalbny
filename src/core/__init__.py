"""
Core functionality for Shalbny.
"""
from .win_api import switch_keyboard_layout, play_feedback_sound
from .text_switcher import TextSwitcher
from .hotkey_service import HotkeyService

__all__ = ["switch_keyboard_layout", "play_feedback_sound", "TextSwitcher", "HotkeyService"]
