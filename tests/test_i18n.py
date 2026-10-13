"""
Unit tests for i18n localization module and new features.
"""
import pytest
from src.i18n import I18n, TRANSLATIONS, i18n
from src.config import ConfigManager, DEFAULT_CONFIG


class TestI18nLocalization:
    """Tests localization dictionary parity and switching."""

    def test_translations_dictionary_parity(self):
        """Verify that every Arabic translation key has a corresponding English key and vice-versa."""
        ar_keys = set(TRANSLATIONS["ar"].keys())
        en_keys = set(TRANSLATIONS["en"].keys())

        missing_in_en = ar_keys - en_keys
        missing_in_ar = en_keys - ar_keys

        assert not missing_in_en, f"Keys in Arabic missing in English: {missing_in_en}"
        assert not missing_in_ar, f"Keys in English missing in Arabic: {missing_in_ar}"

    def test_essential_translation_keys_exist(self):
        """Assert essential UI keys exist in both locales."""
        essential_keys = [
            "app_title",
            "tab_general",
            "tab_shortcut",
            "tab_stats",
            "tab_developer",
            "guide_title",
            "guide_step1",
            "guide_step2",
            "guide_step3",
            "stats_title",
            "stats_count_lbl",
            "stats_reset_btn",
            "reset_defaults_title",
            "reset_defaults_btn",
            "dev_name",
            "github_lbl",
            "linkedin_lbl",
            "phone_lbl",
            "check_updates_btn",
            "tray_app_name",
            "tray_tooltip_running",
            "tray_tooltip_paused",
            "tray_open_settings",
            "tray_guide",
            "tray_hotkey_info",
            "audio_title",
            "sound_theme_lbl",
            "tone_soft_pop",
            "tone_windows_chime",
            "tone_gentle_harmony",
            "tone_mute",
            "test_sound_btn"
        ]
        for key in essential_keys:
            assert key in TRANSLATIONS["ar"], f"Missing key '{key}' in 'ar'"
            assert key in TRANSLATIONS["en"], f"Missing key '{key}' in 'en'"

    def test_audio_engine_themes_and_mute(self):
        """Test audio feedback function works safely with all themes and honors mute."""
        from src.core.win_api import play_feedback_sound, _SOFT_POP_WAV, _GENTLE_HARMONY_WAV

        assert len(_SOFT_POP_WAV) > 1000
        assert len(_GENTLE_HARMONY_WAV) > 1000

        # Should execute safely without exceptions
        play_feedback_sound("soft_pop", enabled=True)
        play_feedback_sound("windows_chime", enabled=True)
        play_feedback_sound("gentle_harmony", enabled=True)
        # Mute option
        play_feedback_sound("mute", enabled=True)
        # Globally disabled
        play_feedback_sound("soft_pop", enabled=False)

    def test_language_switching_and_fallback(self):
        """Test switching locale changes returned strings and falls back cleanly."""
        inst = I18n("ar")
        assert "شقلبني" in inst.t("app_title")
        assert inst.t("lang_switch_btn") == "🌐 English"

        inst.set_language("en")
        assert "Shalbny" in inst.t("app_title")
        assert inst.t("lang_switch_btn") == "🌐 العربية"

        # Invalid key fallback
        assert inst.t("non_existent_key_xyz") == "non_existent_key_xyz"

    def test_config_stats_counter_and_defaults(self):
        """Test conversion counter and factory reset methods on ConfigManager."""
        cfg = ConfigManager()
        initial = cfg.get("conversion_count", 0)

        # Increment
        new_val = cfg.increment_conversion_count()
        assert new_val == initial + 1
        assert cfg.get("conversion_count") == new_val

        # Reset defaults
        cfg.reset_defaults()
        assert cfg.get("conversion_count") == 0
        assert cfg.get("hotkey") == "alt+s"
        assert cfg.get("developer_name") == "KHALED ABDELMONEM"
        assert cfg.get("developer_phone") == "01015362991"
        assert cfg.get("developer_linkedin") == "https://www.linkedin.com/in/khaled-moneam"
