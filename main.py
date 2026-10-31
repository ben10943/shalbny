"""
Main Entry Point for Shalbny.
Usage:
    python main.py              # Starts in background with System Tray icon
    python main.py --settings   # Starts and immediately shows settings window
"""
import sys
import ctypes
from pathlib import Path

# Ensure root directory is in sys.path
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

# Ensure Windows groups taskbar icon and uses Shalbny's official identity
try:
    APP_USER_MODEL_ID = "ben10943.Shalbny.App.1.2.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)
except Exception:
    pass

kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32

ERROR_ALREADY_EXISTS = 183
MUTEX_NAME = "Local\\Shalbny_SingleInstance_App_Mutex"
WAKEUP_EVENT_NAME = "Local\\Shalbny_SingleInstance_Wakeup_Event"
EVENT_MODIFY_STATE = 0x0002
HWND_BROADCAST = 0xFFFF

# Register custom message to wake up settings in existing instance
user32.RegisterWindowMessageW.argtypes = [ctypes.c_wchar_p]
user32.RegisterWindowMessageW.restype = ctypes.c_uint
WM_SHALBNY_SHOW_SETTINGS = user32.RegisterWindowMessageW("Shalbny_ShowSettings_Message")

# Global reference to prevent garbage collection of mutex handle
_app_mutex = None


def acquire_single_instance_mutex() -> bool:
    """
    Ensures only a single instance of Shalbny runs at any given time.
    If another instance is already running, notifies it to show settings and returns False.
    """
    global _app_mutex
    _app_mutex = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    if kernel32.GetLastError() == ERROR_ALREADY_EXISTS:
        # Signal the primary instance's named event to open its settings window
        h_event = kernel32.OpenEventW(EVENT_MODIFY_STATE, False, WAKEUP_EVENT_NAME)
        if h_event:
            kernel32.SetEvent(h_event)
            kernel32.CloseHandle(h_event)
        # Also post broadcast as fallback
        user32.PostMessageW(HWND_BROADCAST, WM_SHALBNY_SHOW_SETTINGS, 0, 0)
        return False
    return True


from src.app import ShalbnyApp


def main():
    if not acquire_single_instance_mutex():
        # Cleanly exit so two instances never fight over global hotkeys
        sys.exit(0)

    show_settings = "--settings" in sys.argv or "-s" in sys.argv
    app = ShalbnyApp()
    app.run(show_settings_on_start=show_settings)


if __name__ == "__main__":
    main()
