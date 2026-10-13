"""
Main Application Coordinator for Shalbny.
Coordinates config, converter profiles, hotkeys, tray icon, and GUI window.
"""
import os
import sys
import threading
from typing import Optional

from .config import ConfigManager
from .converter.manager import ProfileManager
from .core.text_switcher import TextSwitcher
from .core.hotkey_service import HotkeyService
from .ui.tray import TrayIconManager
from .ui.settings_window import SettingsWindow


class ShalbnyApp:
    """Core Application Coordinator."""

    def __init__(self):
        self.config = ConfigManager()
        self.profile_manager = ProfileManager()

        # Set profile from config
        saved_profile = self.config.get("active_profile", "ar_en")
        self.profile_manager.set_active_profile(saved_profile)

        # Core services
        self.text_switcher = TextSwitcher(self.profile_manager, self.config)
        self.is_active = True

        # Hotkey listener
        self.hotkey_service = HotkeyService(self._on_hotkey_pressed)
        current_hotkey = self.config.get("hotkey", "alt+s")
        self.hotkey_service.register(current_hotkey)

        # GUI & Tray
        self.settings_window = SettingsWindow(
            config=self.config,
            profile_manager=self.profile_manager,
            on_hotkey_change=self._on_hotkey_changed,
            on_profile_change=self._on_profile_changed,
            on_language_change=self._on_language_changed
        )

        self.tray = TrayIconManager(
            on_open_settings=self._open_settings,
            on_toggle_pause=self._toggle_pause,
            on_exit=self._exit_app,
            on_open_guide=self._open_guide
        )

    def _on_hotkey_pressed(self) -> None:
        """Called when global hotkey is detected."""
        if not self.is_active:
            return
        self.text_switcher.trigger_inversion()

    def _on_hotkey_changed(self, new_hotkey: str) -> bool:
        """Re-binds the hotkey when updated from settings."""
        return self.hotkey_service.register(new_hotkey)

    def _on_profile_changed(self, profile_id: str) -> None:
        """Updates active profile."""
        self.profile_manager.set_active_profile(profile_id)

    def _on_language_changed(self, new_lang: str) -> None:
        """Updates tray menu and tooltip when language is toggled."""
        self.tray.refresh_menu()

    def _toggle_pause(self) -> bool:
        """Toggles active/paused state."""
        self.is_active = not self.is_active
        return self.is_active

    def _open_settings(self) -> None:
        """Safely opens settings window."""
        if self.settings_window.root and self.settings_window.root.winfo_exists():
            self.settings_window.root.after(0, self.settings_window.show)
        else:
            threading.Thread(target=self.settings_window.show, daemon=True).start()

    def _open_guide(self) -> None:
        """Safely opens settings window focused directly on the Guide & Stats tab."""
        from .i18n import i18n
        guide_tab = i18n.t("tab_stats")
        if self.settings_window.root and self.settings_window.root.winfo_exists():
            self.settings_window.root.after(0, lambda: self.settings_window.show(target_tab=guide_tab))
        else:
            threading.Thread(target=lambda: self.settings_window.show(target_tab=guide_tab), daemon=True).start()

    def _exit_app(self) -> None:
        """Performs clean shutdown."""
        self.hotkey_service.unregister()
        self.tray.stop()
        if self.settings_window.root:
            try:
                self.settings_window.root.quit()
            except Exception:
                pass
        sys.exit(0)

    def run(self, show_settings_on_start: bool = False) -> None:
        """Launches the application."""
        # Start system tray icon detached
        self.tray.run(detached=True)

        if show_settings_on_start:
            self.settings_window.show()
        else:
            # Keep main thread alive waiting for exit signal
            import time
            try:
                while True:
                    time.sleep(1)
            except (KeyboardInterrupt, SystemExit):
                self._exit_app()
