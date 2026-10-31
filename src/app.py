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

        # Hotkey listener with single-instance wakeup hook
        self.hotkey_service = HotkeyService(self._on_hotkey_pressed, on_show_settings=self._open_settings)
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

        # Tray & System Menu
        self.tray = TrayIconManager(
            on_open_settings=self._open_settings,
            on_toggle_pause=self._toggle_pause,
            on_exit=self._exit_app,
            on_open_guide=self._open_guide
        )

        # Silent startup update check (background, non-blocking)
        if self.config.get("check_updates_on_start", True):
            threading.Thread(target=self._startup_update_check, daemon=True).start()

    def _startup_update_check(self) -> None:
        """Silently checks GitHub Releases once at startup and stores any update info."""
        try:
            from .core.updater import check_for_updates
            result = check_for_updates()
            if result.get("status") == "update_available":
                self.settings_window.set_update_info(result)
        except Exception:
            pass

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
        if self.is_active:
            # Re-arm hotkey cleanly upon activation
            current_hotkey = self.config.get("hotkey", "alt+s")
            self.hotkey_service.register(current_hotkey)
        else:
            # Unregister so hotkey does not intercept when paused
            self.hotkey_service.unregister()

        if hasattr(self, "settings_window") and self.settings_window:
            self.settings_window.update_engine_status(self.is_active)

        return self.is_active

    def _open_settings(self, target_tab: Optional[str] = None) -> None:
        """Safely opens settings window in a thread-safe manner."""
        if self.settings_window and self.settings_window.root and self.settings_window.root.winfo_exists():
            self.settings_window.root.after(0, lambda: self.settings_window.show(target_tab))
        else:
            self.settings_window.show(target_tab)

    def _open_guide(self) -> None:
        """Safely opens settings window focused directly on the Guide & Stats tab."""
        from .i18n import i18n
        guide_tab = i18n.t("tab_stats")
        self._open_settings(target_tab=guide_tab)

    def _exit_app(self) -> None:
        """Performs clean shutdown."""
        self.hotkey_service.stop()
        self.tray.stop()
        if self.settings_window and self.settings_window.root and self.settings_window.root.winfo_exists():
            try:
                self.settings_window.root.after(0, self.settings_window.root.destroy)
            except Exception:
                pass
        sys.exit(0)

    def run(self, show_settings_on_start: bool = False) -> None:
        """Launches the application."""
        # Initialize GUI on the main thread (withdrawn until opened)
        self.settings_window.initialize()

        # Start system tray icon detached
        self.tray.run(detached=True)

        if show_settings_on_start:
            self.settings_window.show()

        # Main thread runs the GUI event loop
        try:
            self.settings_window.mainloop()
        except (KeyboardInterrupt, SystemExit):
            self._exit_app()
