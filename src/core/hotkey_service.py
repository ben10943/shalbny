"""
Global hotkey listener service for Shalbny.
Registers system-wide hotkeys and triggers the text switcher.
"""
import keyboard
from typing import Callable, Optional


class HotkeyService:
    """Manages global hotkey registration and callbacks."""

    def __init__(self, callback: Callable[[], None]):
        self.callback = callback
        self.current_hotkey: Optional[str] = None
        self._hook_ref = None

    def register(self, hotkey_str: str) -> bool:
        """
        Registers a new global hotkey (e.g. 'pause', 'ctrl+shift+x', 'alt+q').
        Unregisters any previous hotkey first.
        """
        self.unregister()
        try:
            # Add hotkey with suppress=False to avoid swallowing keys when not matched
            self._hook_ref = keyboard.add_hotkey(hotkey_str, self.callback)
            self.current_hotkey = hotkey_str
            return True
        except Exception:
            return False

    def unregister(self) -> None:
        """Unregisters the current hotkey if active."""
        if self._hook_ref is not None:
            try:
                keyboard.remove_hotkey(self._hook_ref)
            except Exception:
                pass
            self._hook_ref = None
            self.current_hotkey = None
