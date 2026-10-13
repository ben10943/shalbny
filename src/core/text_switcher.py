"""
Text switcher engine for Shalbny.
Handles capturing selected text via clipboard, converting it, and injecting it back.
"""
import time
import threading
import keyboard
import pyperclip
from typing import Optional

from ..converter.manager import ProfileManager
from ..config import ConfigManager
from .win_api import (
    switch_keyboard_layout,
    play_feedback_sound,
    is_line_copy_without_selection,
    send_native_ctrl_c,
    send_native_ctrl_v,
    release_physical_modifiers
)


class TextSwitcher:
    """Orchestrates text inversion for selected text in active window."""

    def __init__(self, profile_manager: ProfileManager, config: ConfigManager):
        self.profile_manager = profile_manager
        self.config = config
        self._lock = threading.Lock()
        self._is_processing = False

    def trigger_inversion(self) -> bool:
        """
        Executes text inversion in a thread-safe worker.
        Returns True if triggered.
        """
        with self._lock:
            if self._is_processing:
                return False
            self._is_processing = True

        # Run in separate thread to prevent blocking global hook
        thread = threading.Thread(target=self._process_inversion, daemon=True)
        thread.start()
        return True

    def _process_inversion(self) -> None:
        try:
            # 1. Back up current clipboard content
            old_clipboard: str = ""
            try:
                old_clipboard = pyperclip.paste()
            except Exception:
                old_clipboard = ""

            # 2. Release physical modifier keys and pause for OS event queue
            release_physical_modifiers()
            time.sleep(0.04)

            # 3. Empty clipboard to accurately detect new copy
            try:
                pyperclip.copy("")
            except Exception:
                pass
            time.sleep(0.03)

            # 4. Simulate native Ctrl+C to copy current selection
            send_native_ctrl_c()

            # 5. Poll for copied text (up to 500ms with instant early exit)
            selected_text = ""
            for _ in range(25):
                time.sleep(0.02)
                try:
                    val = pyperclip.paste()
                    if val:
                        selected_text = val
                        break
                except Exception:
                    pass

            # If nothing was selected or editor copied line without selection, restore clipboard and exit
            if not selected_text or is_line_copy_without_selection():
                if old_clipboard and self.config.get("restore_clipboard", True):
                    try:
                        pyperclip.copy(old_clipboard)
                    except Exception:
                        pass
                return

            # 6. Convert text using active profile
            converted_text = self.profile_manager.convert(selected_text)

            # If no transformation occurred, abort and restore
            if converted_text == selected_text:
                if old_clipboard and self.config.get("restore_clipboard", True):
                    try:
                        pyperclip.copy(old_clipboard)
                    except Exception:
                        pass
                return

            # 7. Place converted text on clipboard and paste natively
            pyperclip.copy(converted_text)
            time.sleep(0.04)
            send_native_ctrl_v()

            # 8. Allow target window time to receive paste
            time.sleep(0.12)

            # 9. Switch OS keyboard input layout if enabled
            if self.config.get("switch_system_language", True):
                switch_keyboard_layout()

            # Record conversion statistics
            try:
                self.config.increment_conversion_count()
            except Exception:
                pass

            # 10. Play feedback sound if enabled
            if self.config.get("play_sound", True):
                sound_theme = self.config.get("sound_theme", "soft_pop")
                play_feedback_sound(sound_theme=sound_theme, enabled=True)

            # 11. Restore previous clipboard content safely after host app finishes paste
            if self.config.get("restore_clipboard", True) and old_clipboard != converted_text:
                time.sleep(0.35)
                try:
                    pyperclip.copy(old_clipboard)
                except Exception:
                    pass

        except Exception:
            pass
        finally:
            with self._lock:
                self._is_processing = False
