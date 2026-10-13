"""
Windows Win32 API interop and native helpers for Shalbny.
Handles keyboard layout switching, active window detection, and feedback sounds.
"""
import ctypes
import winsound
from ctypes import wintypes

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Win32 Constants
WM_INPUTLANGCHANGEREQUEST = 0x0050
HKL_NEXT = 1
HKL_PREV = 0


def get_foreground_window() -> int:
    """Get handle to the currently active foreground window."""
    return user32.GetForegroundWindow()


def switch_keyboard_layout(to_next: bool = True) -> bool:
    """
    Requests the active foreground window to switch its input language layout.
    Sends WM_INPUTLANGCHANGEREQUEST to the foreground window.
    """
    try:
        hwnd = get_foreground_window()
        if not hwnd:
            return False

        hkl_flag = HKL_NEXT if to_next else HKL_PREV
        # Post message to foreground window thread
        user32.PostMessageW(hwnd, WM_INPUTLANGCHANGEREQUEST, 0, hkl_flag)
        return True
    except Exception:
        return False


import io
import wave
import struct
import math


def _generate_soft_pop_wav() -> bytes:
    """Generates an ultra-soft acoustic bubble pop (macOS/iOS style)."""
    buf = io.BytesIO()
    w = wave.open(buf, 'wb')
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(44100)
    samples = []
    duration = 0.05
    n_samples = int(44100 * duration)
    for i in range(n_samples):
        t = i / 44100
        freq = 750 - 400 * (t / duration)
        amp = 12000 * math.exp(-t / 0.014)
        val = int(amp * math.sin(2 * math.pi * freq * t))
        samples.append(max(-32767, min(32767, val)))
    w.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
    w.close()
    return buf.getvalue()


def _generate_gentle_harmony_wav() -> bytes:
    """Generates a warm, subtle musical confirmation chord."""
    buf = io.BytesIO()
    w = wave.open(buf, 'wb')
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(44100)
    samples = []
    duration = 0.08
    n_samples = int(44100 * duration)
    for i in range(n_samples):
        t = i / 44100
        env = math.exp(-t / 0.03)
        val1 = 6000 * math.sin(2 * math.pi * 523.25 * t)  # C5
        val2 = 5000 * math.sin(2 * math.pi * 659.25 * t)  # E5
        val = int((val1 + val2) * env)
        samples.append(max(-32767, min(32767, val)))
    w.writeframes(struct.pack('<' + 'h' * len(samples), *samples))
    w.close()
    return buf.getvalue()


_SOFT_POP_WAV = _generate_soft_pop_wav()
_GENTLE_HARMONY_WAV = _generate_gentle_harmony_wav()


def play_feedback_sound(sound_theme: str = "soft_pop", enabled: bool = True) -> None:
    """
    Play a discreet, pleasant audio cue.
    Supports asynchronous non-blocking playback with zero CPU lag.
    """
    if not enabled or sound_theme == "mute":
        return

    try:
        if sound_theme == "windows_chime":
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        elif sound_theme == "gentle_harmony":
            winsound.PlaySound(_GENTLE_HARMONY_WAV, winsound.SND_MEMORY | winsound.SND_ASYNC)
        else:
            # Default to ultra-soft pop
            winsound.PlaySound(_SOFT_POP_WAV, winsound.SND_MEMORY | winsound.SND_ASYNC)
    except Exception:
        pass


def is_line_copy_without_selection() -> bool:
    """
    Checks if clipboard content is an automatic whole-line copy triggered by
    editors like VS Code / Visual Studio when no text is explicitly selected.
    """
    try:
        if not user32.OpenClipboard(0):
            return False
        try:
            fmt = 0
            while True:
                fmt = user32.EnumClipboardFormats(fmt)
                if not fmt:
                    break
                buf = ctypes.create_unicode_buffer(256)
                user32.GetClipboardFormatNameW(fmt, buf, 256)
                name = buf.value
                if "VisualStudioEditorOperationsLineCutCopyClipboardTag" in name or "MSDEV-ColumnSelect-Marker" in name:
                    return True
            return False
        finally:
            user32.CloseClipboard()
    except Exception:
        return False


# Win32 Virtual Key Codes
VK_SHIFT = 0x10
VK_CONTROL = 0x11
VK_MENU = 0x12       # Alt key
VK_C = 0x43
VK_V = 0x56
KEYEVENTF_KEYUP = 0x0002


def release_physical_modifiers() -> None:
    """Forces release of modifier keys (Ctrl, Alt, Shift) in Windows input queue."""
    for vk in (VK_MENU, VK_CONTROL, VK_SHIFT):
        user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)


def send_native_ctrl_c() -> None:
    """Sends native Win32 Ctrl+C to copy selected text with zero race conditions."""
    release_physical_modifiers()
    # Press Ctrl down
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    # Press C down & up
    user32.keybd_event(VK_C, 0, 0, 0)
    user32.keybd_event(VK_C, 0, KEYEVENTF_KEYUP, 0)
    # Release Ctrl
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)


def send_native_ctrl_v() -> None:
    """Sends native Win32 Ctrl+V to paste converted text cleanly."""
    release_physical_modifiers()
    # Press Ctrl down
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    # Press V down & up
    user32.keybd_event(VK_V, 0, 0, 0)
    user32.keybd_event(VK_V, 0, KEYEVENTF_KEYUP, 0)
    # Release Ctrl
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

