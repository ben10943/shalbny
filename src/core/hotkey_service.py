"""
Global hotkey listener service for Shalbny.
Registers system-wide hotkeys and triggers the text switcher.

Architecture:
- Primary: Win32 native RegisterHotKey tied to a dedicated thread message pump.
  Zero hook latency, zero CPU overhead, and complete immunity to Windows LowLevelHooksTimeout.
- Sleep & Idle Resilience:
  1. Wall-Clock Watchdog detects system suspension / Modern Standby time jumps (>2.5s)
     and immediately re-registers the hotkey upon wake.
  2. Heartbeat Refresh: Proactively re-registers the hotkey every 30 seconds during long idle.
  3. Thread Guardian: Auto-detects if the background message pump thread ever terminates
     and seamlessly resurrects it.
- Single Instance Interop:
  Listens for WM_SHALBNY_SHOW_SETTINGS broadcast to bring the settings window to the front
  if a second instance is launched.
- Fallback: Gracefully falls back to the keyboard library if a conflict occurs,
  with automatic hook re-arming on wake.
"""
import ctypes
from ctypes import wintypes
import logging
import threading
import time
from typing import Callable, Optional, Tuple

logger = logging.getLogger("Shalbny.HotkeyService")

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Configure Win32 API signatures for thread message pump
user32.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, ctypes.c_uint, ctypes.c_uint]
user32.RegisterHotKey.restype = wintypes.BOOL

user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
user32.UnregisterHotKey.restype = wintypes.BOOL

user32.PostThreadMessageW.argtypes = [wintypes.DWORD, ctypes.c_uint, wintypes.WPARAM, wintypes.LPARAM]
user32.PostThreadMessageW.restype = wintypes.BOOL

user32.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, ctypes.c_uint, ctypes.c_uint, ctypes.c_uint]
user32.PeekMessageW.restype = wintypes.BOOL

user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, ctypes.c_uint, ctypes.c_uint]
user32.GetMessageW.restype = wintypes.BOOL

user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.TranslateMessage.restype = wintypes.BOOL

user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
user32.DispatchMessageW.restype = ctypes.c_int64

user32.VkKeyScanW.argtypes = [wintypes.WCHAR]
user32.VkKeyScanW.restype = ctypes.c_short

user32.RegisterWindowMessageW.argtypes = [wintypes.LPCWSTR]
user32.RegisterWindowMessageW.restype = ctypes.c_uint

# Win32 Constants
WM_QUIT = 0x0012
WM_HOTKEY = 0x0312
WM_APP = 0x8000

WM_APP_REGISTER = WM_APP + 1
WM_APP_UNREGISTER = WM_APP + 2
WM_APP_REFRESH = WM_APP + 3

WM_SHALBNY_SHOW_SETTINGS = user32.RegisterWindowMessageW("Shalbny_ShowSettings_Message")
WAKEUP_EVENT_NAME = "Local\\Shalbny_SingleInstance_Wakeup_Event"

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

HOTKEY_ID = 0x5348  # 'SH'

AR_TO_EN_KEY_MAP = {
    'ذ': '`', 'ض': 'q', 'ص': 'w', 'ث': 'e', 'ق': 'r', 'ف': 't', 'غ': 'y',
    'ع': 'u', 'ه': 'i', 'خ': 'o', 'ح': 'p', 'ج': '[', 'د': ']',
    'ش': 'a', 'س': 's', 'ي': 'd', 'ب': 'f', 'ل': 'g', 'ا': 'h',
    'ت': 'j', 'ن': 'k', 'م': 'l', 'ك': ';', 'ط': "'",
    'ئ': 'z', 'ء': 'x', 'ؤ': 'c', 'ر': 'v', 'ى': 'n',
    'ة': 'm', 'و': ',', 'ز': '.', 'ظ': '/',
    'ّ': '~', 'َ': 'q', 'ً': 'w', 'ُ': 'e', 'ٌ': 'r', 'لإ': 't', 'إ': 'y',
    '‘': 'u', '÷': 'i', '×': 'o', '؛': 'p', 'ِ': 'a', 'ٍ': 's', 'أ': 'h',
    'ـ': 'j', '،': 'k', 'ْ': 'x', 'آ': 'n', '’': 'm', '؟': '?',
    'الت': 'alt', 'ألت': 'alt', 'كنترول': 'ctrl', 'شفت': 'shift', 'ويندوز': 'win'
}

VK_MAP = {
    'space': 0x20,
    'page up': 0x21, 'pageup': 0x21, 'prior': 0x21,
    'page down': 0x22, 'pagedown': 0x22, 'next': 0x22,
    'end': 0x23,
    'home': 0x24,
    'left': 0x25,
    'up': 0x26,
    'right': 0x27,
    'down': 0x28,
    'print screen': 0x2C, 'printscreen': 0x2C, 'prtsc': 0x2C,
    'insert': 0x2D,
    'delete': 0x2E, 'del': 0x2E,
    'tab': 0x09,
    'enter': 0x0D, 'return': 0x0D,
    'escape': 0x1B, 'esc': 0x1B,
    'backspace': 0x08,
    'pause': 0x13,
    'caps lock': 0x14, 'capslock': 0x14,
    'num lock': 0x90, 'numlock': 0x90,
    'scroll lock': 0x91, 'scrolllock': 0x91,
    **{f'f{i}': 0x70 + (i - 1) for i in range(1, 25)},
}


def parse_hotkey_string(hotkey_str: str) -> Optional[Tuple[int, int]]:
    """
    Parses a hotkey string like 'alt+s', 'ctrl+shift+x', 'f8', 'pause'
    into (modifiers, vk_code).
    Automatically maps Arabic keyboard layouts and ensures Virtual Key codes
    are strictly within valid Win32 8-bit range (0x01..0xFF).
    """
    if not hotkey_str:
        return None

    raw_parts = [AR_TO_EN_KEY_MAP.get(p.strip().lower(), p.strip().lower())
                 for p in hotkey_str.split('+') if p.strip()]
    if not raw_parts:
        return None

    modifiers = MOD_NOREPEAT
    key_part = None

    for part in raw_parts:
        if part in ('alt', 'menu'):
            modifiers |= MOD_ALT
        elif part in ('ctrl', 'control'):
            modifiers |= MOD_CONTROL
        elif part in ('shift',):
            modifiers |= MOD_SHIFT
        elif part in ('win', 'windows', 'super'):
            modifiers |= MOD_WIN
        else:
            key_part = part

    if not key_part:
        return None

    # Resolve virtual key code
    if key_part in VK_MAP:
        vk = VK_MAP[key_part]
    elif len(key_part) == 1:
        # Strictly Latin ASCII letters only to prevent non-ASCII Unicode ord() corruption
        if 'a' <= key_part <= 'z' or 'A' <= key_part <= 'Z':
            vk = ord(key_part.upper())
        elif key_part.isdigit():
            vk = ord(key_part)
        else:
            scan = user32.VkKeyScanW(key_part)
            if scan == -1:
                return None
            vk = scan & 0xFF
    else:
        return None

    # Safety: Virtual Key codes in Windows are 8-bit unsigned integers (1..255)
    if not (0 < vk <= 255):
        return None

    return modifiers, vk


class HotkeyService:
    """
    Manages global hotkey registration, system wake recovery, and callbacks.
    Employs native Win32 RegisterHotKey as primary engine with automatic sleep/wake
    recovery, and falls back to keyboard library if conflicts arise.
    """

    def __init__(
        self,
        callback: Callable[[], None],
        on_show_settings: Optional[Callable[[], None]] = None,
        wakeup_event_name: Optional[str] = None
    ):
        self.callback = callback
        self.on_show_settings = on_show_settings
        self.current_hotkey: Optional[str] = None
        self._parsed_binding: Optional[Tuple[int, int]] = None

        self._thread_id: Optional[int] = None
        self._ready_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

        self._action_done = threading.Event()
        self._action_result = False

        self._last_trigger_time = 0.0
        self._lock = threading.Lock()

        # Fallback hook reference if keyboard module is used
        self._fallback_hook = None

        # Start background Win32 message thread
        self._start_message_thread()

        # Start watchdog thread
        self._stop_watchdog = threading.Event()
        self._watchdog_thread = threading.Thread(
            target=self._watchdog_loop,
            name="ShalbnySleepWatchdog",
            daemon=True
        )
        self._watchdog_thread.start()

        # Single-instance inter-process wakeup listener via Win32 Named Event
        self._wakeup_event_name = wakeup_event_name or WAKEUP_EVENT_NAME
        self._wakeup_event_handle = kernel32.CreateEventW(None, False, False, self._wakeup_event_name)
        self._stop_wakeup_listener = threading.Event()
        self._wakeup_listener_thread = threading.Thread(
            target=self._wakeup_listener_loop,
            name="ShalbnyWakeupListener",
            daemon=True
        )
        self._wakeup_listener_thread.start()

    def _wakeup_listener_loop(self) -> None:
        """Listens for wakeup events from subsequent launches to show settings GUI."""
        if not self._wakeup_event_handle:
            return
        while not self._stop_wakeup_listener.is_set():
            res = kernel32.WaitForSingleObject(self._wakeup_event_handle, 500)
            if res == 0:  # WAIT_OBJECT_0
                self._safe_show_settings()

    def _start_message_thread(self) -> None:
        self._ready_event.clear()
        self._thread = threading.Thread(
            target=self._message_loop,
            name="ShalbnyHotkeyThread",
            daemon=True
        )
        self._thread.start()
        # Wait until message pump is initialized
        self._ready_event.wait(timeout=3.0)

    def _safe_callback(self) -> None:
        try:
            self.callback()
        except Exception:
            pass

    def _safe_show_settings(self) -> None:
        if self.on_show_settings:
            try:
                self.on_show_settings()
            except Exception:
                pass

    def _message_loop(self) -> None:
        self._thread_id = kernel32.GetCurrentThreadId()

        # Force creation of message queue by peeking without blocking
        msg = wintypes.MSG()
        user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, 0)
        self._ready_event.set()

        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_HOTKEY:
                if msg.wParam == HOTKEY_ID:
                    now = time.monotonic()
                    # 150ms debounce to prevent key bounce
                    if now - self._last_trigger_time >= 0.15:
                        self._last_trigger_time = now
                        threading.Thread(target=self._safe_callback, daemon=True).start()

            elif msg.message == WM_SHALBNY_SHOW_SETTINGS:
                threading.Thread(target=self._safe_show_settings, daemon=True).start()

            elif msg.message == WM_APP_REGISTER:
                user32.UnregisterHotKey(None, HOTKEY_ID)
                if self._parsed_binding:
                    mods, vk = self._parsed_binding
                    ok = user32.RegisterHotKey(None, HOTKEY_ID, mods, vk)
                    self._action_result = bool(ok)
                else:
                    self._action_result = True
                self._action_done.set()

            elif msg.message == WM_APP_UNREGISTER:
                user32.UnregisterHotKey(None, HOTKEY_ID)
                self._action_result = True
                self._action_done.set()

            elif msg.message == WM_APP_REFRESH:
                user32.UnregisterHotKey(None, HOTKEY_ID)
                if self._parsed_binding:
                    mods, vk = self._parsed_binding
                    # Retry registration up to 3 times in case of transient lock during wake
                    for _ in range(3):
                        if user32.RegisterHotKey(None, HOTKEY_ID, mods, vk):
                            break
                        time.sleep(0.05)

            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        user32.UnregisterHotKey(None, HOTKEY_ID)
        self._thread_id = None

    def _on_system_wake(self, source: str) -> None:
        """Called upon system power resume or heartbeat to re-arm the hotkey."""
        with self._lock:
            if self._parsed_binding and self._thread_id:
                user32.PostThreadMessageW(self._thread_id, WM_APP_REFRESH, 0, 0)
            elif self._fallback_hook and self.current_hotkey:
                self._rearm_fallback_hook()

    def _watchdog_loop(self) -> None:
        """
        Wall-clock watchdog:
        - Detects system sleep / Modern Standby (time jump > 2.5s).
        - Periodically re-arms the hotkey every 30s during long idle.
        - Resurrects message pump thread if ever terminated.
        """
        last_time = time.monotonic()
        heartbeat_counter = 0

        while not self._stop_watchdog.is_set():
            time.sleep(1.0)
            now = time.monotonic()
            elapsed = now - last_time
            last_time = now

            heartbeat_counter += 1

            # 1. Thread guardian: resurrect if thread died
            if not self._thread or not self._thread.is_alive():
                self._start_message_thread()
                if self.current_hotkey:
                    self.register(self.current_hotkey)

            # 2. System wake detection: elapsed > 2.5s while sleeping 1.0s
            if elapsed > 2.5:
                self._on_system_wake("wall_clock_wake")
                heartbeat_counter = 0
            # 3. Periodic refresh: every 30 seconds to prevent state staleness
            elif heartbeat_counter >= 30:
                heartbeat_counter = 0
                self._on_system_wake("periodic_heartbeat")

    def register(self, hotkey_str: str) -> bool:
        """
        Registers a new global hotkey (e.g. 'alt+s', 'ctrl+shift+x', 'pause').
        Unregisters any previous hotkey first.
        First attempts native Win32 RegisterHotKey; falls back to keyboard library if needed.
        """
        self.unregister()

        if not hotkey_str:
            return False

        with self._lock:
            self.current_hotkey = hotkey_str
            parsed = parse_hotkey_string(hotkey_str)
            self._parsed_binding = parsed

            # Attempt native RegisterHotKey via thread message
            if parsed and self._thread_id:
                self._action_done.clear()
                user32.PostThreadMessageW(self._thread_id, WM_APP_REGISTER, 0, 0)
                if self._action_done.wait(timeout=1.0) and self._action_result:
                    return True

            # Fallback to keyboard library
            return self._register_fallback(hotkey_str)

    def _register_fallback(self, hotkey_str: str) -> bool:
        try:
            import keyboard
            self._fallback_hook = keyboard.add_hotkey(hotkey_str, self.callback)
            return True
        except Exception:
            self._fallback_hook = None
            return False

    def _rearm_fallback_hook(self) -> None:
        if not self.current_hotkey:
            return
        try:
            import keyboard
            if self._fallback_hook:
                try:
                    keyboard.remove_hotkey(self._fallback_hook)
                except Exception:
                    pass
            self._fallback_hook = keyboard.add_hotkey(self.current_hotkey, self.callback)
        except Exception:
            pass

    def unregister(self) -> None:
        """Unregisters the current hotkey if active."""
        with self._lock:
            self.current_hotkey = None
            self._parsed_binding = None

            if self._thread_id:
                self._action_done.clear()
                user32.PostThreadMessageW(self._thread_id, WM_APP_UNREGISTER, 0, 0)
                self._action_done.wait(timeout=0.5)

            if self._fallback_hook:
                try:
                    import keyboard
                    keyboard.remove_hotkey(self._fallback_hook)
                except Exception:
                    pass
                self._fallback_hook = None

    def stop(self) -> None:
        """Shuts down background threads cleanly."""
        self.unregister()
        self._stop_watchdog.set()
        self._stop_wakeup_listener.set()

        if self._wakeup_event_handle:
            try:
                kernel32.SetEvent(self._wakeup_event_handle)
                kernel32.CloseHandle(self._wakeup_event_handle)
            except Exception:
                pass
            self._wakeup_event_handle = None

        tid = self._thread_id
        if tid:
            user32.PostThreadMessageW(tid, WM_QUIT, 0, 0)

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

    def __del__(self) -> None:
        try:
            self.stop()
        except Exception:
            pass
