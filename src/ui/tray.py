"""
System Tray icon and background service integration for Shalbny.
Provides discreet system tray presence with clean executive menu actions
and high-contrast, razor-sharp luminous status indicators.
"""
import pystray
from PIL import Image
from typing import Callable, Optional
from pathlib import Path
from .assets import create_tray_icon
from ..i18n import i18n


class TrayIconManager:
    """Manages the Windows System Tray icon and executive context menu."""

    def __init__(
        self,
        on_open_settings: Callable[[], None],
        on_toggle_pause: Callable[[], bool],
        on_exit: Callable[[], None],
        on_open_guide: Optional[Callable[[], None]] = None
    ):
        self.on_open_settings = on_open_settings
        self.on_toggle_pause = on_toggle_pause
        self.on_exit = on_exit
        self.on_open_guide = on_open_guide or on_open_settings

        self.is_paused = False
        self.icon: Optional[pystray.Icon] = None

    def _get_tooltip(self) -> str:
        key = "tray_tooltip_paused" if self.is_paused else "tray_tooltip_running"
        return i18n.t(key)

    def _get_pause_resume_text(self, item) -> str:
        return i18n.t("tray_resume") if self.is_paused else i18n.t("tray_pause")

    def _toggle_pause_action(self, icon, item) -> None:
        self.is_paused = not self.on_toggle_pause()
        if self.icon:
            self.icon.icon = create_tray_icon(is_paused=self.is_paused)
            self.icon.title = self._get_tooltip()
            self.icon.update_menu()

    def _open_settings_action(self, icon, item) -> None:
        self.on_open_settings()

    def _open_guide_action(self, icon, item) -> None:
        self.on_open_guide()

    def _exit_action(self, icon, item) -> None:
        if self.icon:
            self.icon.stop()
        self.on_exit()

    def refresh_menu(self) -> None:
        """Refreshes tray menu items and tooltip with active language."""
        if self.icon:
            try:
                self.icon.title = self._get_tooltip()
                self.icon.update_menu()
            except Exception:
                pass

    def build_menu(self) -> pystray.Menu:
        """Builds clean, professional context menu without ugly pixelated emojis."""
        return pystray.Menu(
            pystray.MenuItem(lambda item: i18n.t("tray_open_settings"), self._open_settings_action, default=True),
            pystray.MenuItem(lambda item: i18n.t("tray_guide"), self._open_guide_action),
            pystray.MenuItem(lambda item: i18n.t("tray_hotkey_info"), self._open_settings_action),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(self._get_pause_resume_text, self._toggle_pause_action),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(lambda item: i18n.t("tray_exit"), self._exit_action)
        )

    def run(self, detached: bool = True) -> None:
        """Launches the system tray icon with crisp high-contrast icon."""
        image = create_tray_icon(is_paused=False, size=64)
        self.icon = pystray.Icon(
            name="Shalbny",
            icon=image,
            title=self._get_tooltip(),
            menu=self.build_menu()
        )
        if detached:
            self.icon.run_detached()
        else:
            self.icon.run()

    def stop(self) -> None:
        """Stops the tray icon."""
        if self.icon:
            self.icon.stop()
