"""
Unit tests for HotkeyService and Win32 Native Hotkey Registration.
"""
import pytest
import time
from src.core.hotkey_service import (
    HotkeyService,
    parse_hotkey_string,
    MOD_ALT,
    MOD_CONTROL,
    MOD_SHIFT,
    MOD_WIN,
    MOD_NOREPEAT
)


class TestHotkeyParser:

    def test_parse_alt_s(self):
        parsed = parse_hotkey_string("alt+s")
        assert parsed is not None
        mods, vk = parsed
        assert mods == (MOD_ALT | MOD_NOREPEAT)
        assert vk == ord('S')

    def test_parse_ctrl_alt_s(self):
        parsed = parse_hotkey_string("ctrl+alt+s")
        assert parsed is not None
        mods, vk = parsed
        assert mods == (MOD_CONTROL | MOD_ALT | MOD_NOREPEAT)
        assert vk == ord('S')

    def test_parse_ctrl_shift_x(self):
        parsed = parse_hotkey_string("ctrl+shift+x")
        assert parsed is not None
        mods, vk = parsed
        assert mods == (MOD_CONTROL | MOD_SHIFT | MOD_NOREPEAT)
        assert vk == ord('X')

    def test_parse_function_keys(self):
        for i in range(1, 13):
            parsed = parse_hotkey_string(f"f{i}")
            assert parsed is not None
            mods, vk = parsed
            assert mods == MOD_NOREPEAT
            assert vk == 0x70 + (i - 1)

    def test_parse_special_keys(self):
        specials = {
            "pause": 0x13,
            "insert": 0x2D,
            "delete": 0x2E,
            "home": 0x24,
            "end": 0x23,
            "pageup": 0x21,
            "pagedown": 0x22,
            "space": 0x20,
            "tab": 0x09,
        }
        for name, expected_vk in specials.items():
            parsed = parse_hotkey_string(name)
            assert parsed is not None
            mods, vk = parsed
            assert vk == expected_vk

    def test_parse_invalid(self):
        assert parse_hotkey_string("") is None
        assert parse_hotkey_string("unknown_key_xyz_123") is None
        assert parse_hotkey_string("ctrl+alt") is None  # only modifiers, no key

    def test_parse_arabic_keyboard_layouts(self):
        # 'س' corresponds to physical 'S'
        parsed_alt_seen = parse_hotkey_string("alt+س")
        assert parsed_alt_seen is not None
        assert parsed_alt_seen == (MOD_ALT | MOD_NOREPEAT, ord('S'))

        # 'ctrl+س' corresponds to 'ctrl+s'
        parsed_ctrl_seen = parse_hotkey_string("ctrl+س")
        assert parsed_ctrl_seen is not None
        assert parsed_ctrl_seen == (MOD_CONTROL | MOD_NOREPEAT, ord('S'))

        # 'ش' corresponds to physical 'A'
        parsed_alt_sheen = parse_hotkey_string("alt+ش")
        assert parsed_alt_sheen is not None
        assert parsed_alt_sheen == (MOD_ALT | MOD_NOREPEAT, ord('A'))

        # Arabic modifier names: 'الت+س'
        parsed_arabic_mod = parse_hotkey_string("الت+س")
        assert parsed_arabic_mod is not None
        assert parsed_arabic_mod == (MOD_ALT | MOD_NOREPEAT, ord('S'))


class TestHotkeyServiceLifecycle:

    def test_service_initialization_and_registration(self):
        triggered = []

        def dummy_cb():
            triggered.append(True)

        service = HotkeyService(dummy_cb)
        try:
            # Register Alt+S
            success = service.register("alt+s")
            assert success is True
            assert service.current_hotkey == "alt+s"

            # Simulate system wake
            service._on_system_wake("unit_test")
            assert service.current_hotkey == "alt+s"

            # Unregister
            service.unregister()
            assert service.current_hotkey is None
        finally:
            service.stop()

    def test_service_switch_hotkey(self):
        service = HotkeyService(lambda: None)
        try:
            assert service.register("alt+s") is True
            assert service.current_hotkey == "alt+s"

            # Switch to Alt+Q
            assert service.register("alt+q") is True
            assert service.current_hotkey == "alt+q"
        finally:
            service.stop()

    def test_service_stop_idempotent(self):
        service = HotkeyService(lambda: None)
        service.stop()
        # Second stop should not raise error
        service.stop()

    def test_service_on_show_settings(self):
        show_called = []
        service = HotkeyService(lambda: None, on_show_settings=lambda: show_called.append(True))
        try:
            service._safe_show_settings()
            assert len(show_called) == 1
        finally:
            service.stop()

    def test_service_periodic_heartbeat_dispatch(self):
        service = HotkeyService(lambda: None)
        try:
            service.register("alt+s")
            # Trigger heartbeat
            service._on_system_wake("periodic_heartbeat")
            time.sleep(0.1)
            assert service.current_hotkey == "alt+s"
        finally:
            service.stop()

    def test_service_named_event_wakeup(self):
        import ctypes
        import os
        from src.core.hotkey_service import WAKEUP_EVENT_NAME
        kernel32 = ctypes.windll.kernel32
        wake_calls = []
        test_event_name = f"{WAKEUP_EVENT_NAME}_test_{os.getpid()}"

        service = HotkeyService(
            lambda: None,
            on_show_settings=lambda: wake_calls.append(True),
            wakeup_event_name=test_event_name
        )
        try:
            time.sleep(0.1)
            # Open the named event from another context and signal it
            h_event = kernel32.OpenEventW(0x0002, False, test_event_name)
            assert h_event != 0
            kernel32.SetEvent(h_event)
            kernel32.CloseHandle(h_event)

            # Wait for wakeup listener to receive it
            time.sleep(0.3)
            assert len(wake_calls) >= 1
        finally:
            service.stop()
