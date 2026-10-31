"""
Unit tests for the Shalbny rescue history feature (ConfigManager).
Uses an isolated temp config file so the real user configuration is untouched.
"""
import json
import pytest

import src.config as config_module
from src.config import ConfigManager


@pytest.fixture
def manager(tmp_path, monkeypatch):
    """Provides a ConfigManager bound to an isolated temporary config file."""
    config_file = tmp_path / "config.json"
    config_dir = tmp_path
    monkeypatch.setattr(config_module, "CONFIG_FILE", config_file)
    monkeypatch.setattr(config_module, "CONFIG_DIR", config_dir)
    return ConfigManager()


class TestRescueHistory:

    def test_history_starts_empty(self, manager):
        assert manager.get_history() == []

    def test_add_history_appends_entries(self, manager):
        manager.add_history("اثممخ", "hello")
        manager.add_history("hgsghl ugd;l", "السلام عليكم")
        history = manager.get_history()
        assert len(history) == 2
        # Newest first
        assert history[0]["original"] == "hgsghl ugd;l"
        assert history[1]["original"] == "اثممخ"

    def test_history_entry_structure(self, manager):
        manager.add_history("abc", "xyz")
        entry = manager.get_history()[0]
        assert set(entry.keys()) == {"t", "original", "converted"}
        assert entry["converted"] == "xyz"

    def test_history_respects_max_items(self, manager):
        for i in range(15):
            manager.add_history(f"src{i}", f"dst{i}")
        history = manager.get_history()
        assert len(history) == 10  # newest 10 kept
        assert history[0]["original"] == "src14"

    def test_history_truncates_long_text(self, manager):
        long_text = "x" * 1000
        manager.add_history(long_text, "ok")
        assert len(manager.get_history()[0]["original"]) == 160

    def test_clear_history(self, manager):
        manager.add_history("a", "b")
        manager.clear_history()
        assert manager.get_history() == []

    def test_history_persists_to_disk(self, manager, tmp_path):
        manager.add_history("صخقمي", "world")
        with open(config_module.CONFIG_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        assert saved["history"][0]["converted"] == "world"

    def test_add_history_does_not_touch_other_settings(self, manager):
        manager.set("hotkey", "ctrl+alt+z")
        manager.add_history("a", "b")
        assert manager.get("hotkey") == "ctrl+alt+z"

    def test_check_updates_on_start_defaults_true(self, manager):
        assert manager.get("check_updates_on_start") is True
