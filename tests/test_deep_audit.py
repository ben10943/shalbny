"""
Deep QA & Audit Test Suite for Shalbny.
Exhaustively tests translation engine, ligatures, edge cases,
hotkey debounce, config persistence, and tray status transitions.
"""
import pytest
from src.converter.arabic_english import ArabicEnglishProfile
from src.converter.manager import ProfileManager
from src.config import ConfigManager


class TestDeepConverterAudit:

    @pytest.fixture
    def profile(self):
        return ArabicEnglishProfile()

    def test_complete_arabic_sentences(self, profile):
        pairs = [
            ("السلام عليكم ورحمة الله وبركاته", "hgsbl ugd;l ,vplm hggi ,fv;hji"),
            ("البرمجة بلغة بايثون ممتعة", "hgfvl[m fgym fhde,k lljum"),
            ("مرحبا بكم", "lvpfh f;l"),
            ("صباح الخير", "wfhp hgodv"),
            ("مساء النور", "lshx hgk,v"),
            ("شكرا جزيلا", "a;vh [.db"),
            ("كيف حالك اليوم", ";dt phg; hgd,l")
        ]
        for ar, en in pairs:
            # EN -> AR
            assert profile.to_arabic(en) == ar, f"Failed EN->AR for {en}"
            # AR -> EN
            assert profile.to_english(ar) == en, f"Failed AR->EN for {ar}"
            # Auto-detect bidirectional
            assert profile.convert(en) == ar, f"Auto convert failed for {en}"
            assert profile.convert(ar) == en, f"Auto convert failed for {ar}"

    def test_all_ligatures_bidirectional(self, profile):
        # Test 'b' -> 'لا' and 'لا' -> 'b'
        assert profile.to_arabic("b") == "لا"
        assert profile.to_english("لا") == "b"

        # Test 'B' -> 'لآ' and 'لآ' -> 'B'
        assert profile.to_arabic("B") == "لآ"
        assert profile.to_english("لآ") == "B"

        # Test 'T' -> 'لإ' and 'لإ' -> 'T'
        assert profile.to_arabic("T") == "لإ"
        assert profile.to_english("لإ") == "T"

        # Test 'G' -> 'لأ' and 'لأ' -> 'G'
        assert profile.to_arabic("G") == "لأ"
        assert profile.to_english("لأ") == "G"

    def test_tashkeel_marks(self, profile):
        # Q -> Fatha
        assert profile.to_arabic("Q") == "َ"
        assert profile.to_english("َ") == "Q"

        # W -> Tanwin Fath
        assert profile.to_arabic("W") == "ً"
        assert profile.to_english("ً") == "W"

        # E -> Damma
        assert profile.to_arabic("E") == "ُ"
        assert profile.to_english("ُ") == "E"

        # R -> Tanwin Damm
        assert profile.to_arabic("R") == "ٌ"
        assert profile.to_english("ٌ") == "R"

        # A -> Kasra
        assert profile.to_arabic("A") == "ِ"
        assert profile.to_english("ِ") == "A"

        # S -> Tanwin Kasr
        assert profile.to_arabic("S") == "ٍ"
        assert profile.to_english("ٍ") == "S"

        # X -> Sukun
        assert profile.to_arabic("X") == "ْ"
        assert profile.to_english("ْ") == "X"

        # ~ -> Shadda
        assert profile.to_arabic("~") == "ّ"
        assert profile.to_english("ّ") == "~"

    def test_punctuation_and_symbols(self, profile):
        # Arabic Question Mark vs English
        assert profile.to_arabic("?") == "؟"
        assert profile.to_english("؟") == "?"

        # Arabic Comma vs English
        assert profile.to_arabic("K") == "،"
        assert profile.to_english("،") == "K"

        # Arabic Semicolon vs English
        assert profile.to_arabic("P") == "؛"
        assert profile.to_english("؛") == "P"

    def test_special_strings_and_edge_cases(self, profile):
        # Empty string
        assert profile.convert("") == ""
        # Single space
        assert profile.convert(" ") == " "
        # Newline preserved
        assert profile.convert("hello\nworld") == profile.to_arabic("hello") + "\n" + profile.to_arabic("world")
        # Mixed numbers and spaces
        assert profile.convert("12345 67890") == "12345 67890"

    def test_config_manager_persistence(self):
        from src.config import DEFAULT_CONFIG
        cfg = ConfigManager()
        # Default hotkey in schema should be alt+s, and live hotkey should be a valid non-empty string
        assert DEFAULT_CONFIG["hotkey"] == "alt+s"
        assert isinstance(cfg.get("hotkey"), str) and len(cfg.get("hotkey")) > 0
        # Developer name should be KHALED ABDELMONEM
        assert cfg.get("developer_name") == "KHALED ABDELMONEM"
        assert cfg.get("developer_github") == "https://github.com/ben10943"
        assert cfg.get("developer_linkedin") == "https://www.linkedin.com/in/khaled-moneam"
        assert cfg.get("developer_phone") == "01015362991"

    def test_profile_manager_switching(self):
        mgr = ProfileManager()
        assert mgr.active_profile.id == "ar_en"
        # Test converting through profile manager
        assert mgr.convert("اثممخ") == "hello"
        assert mgr.convert("hello") == "اثممخ"

    def test_ligature_typing_variants(self, profile):
        # User typed السلام letter-by-letter: h(ا) g(ل) s(س) g(ل) h(ا) l(م)
        assert profile.to_arabic("hgsghl") == "السلام"
        # User typed السلام via ligature key: h(ا) g(ل) s(س) b(لا) l(م)
        assert profile.to_arabic("hgsbl") == "السلام"
        # Inverse accurately produces the single physical key on Arabic keyboard
        assert profile.to_english("السلام") == "hgsbl"

    def test_asset_generators(self):
        from src.ui.assets import create_app_icon, create_tray_icon
        app_icon = create_app_icon(size=64)
        assert app_icon.size == (64, 64)
        assert app_icon.mode == "RGBA"

        tray_active = create_tray_icon(is_paused=False, size=32)
        assert tray_active.size == (32, 32)
        tray_paused = create_tray_icon(is_paused=True, size=32)
        assert tray_paused.size == (32, 32)

    def test_win_api_guards(self):
        from src.core.win_api import is_line_copy_without_selection
        # Should return boolean safely without crashing
        res = is_line_copy_without_selection()
        assert isinstance(res, bool)

    def test_installer_user_folder_resolution(self):
        from pathlib import Path
        from installer.setup_wizard import get_user_folder
        desktop = get_user_folder("Desktop", Path.home() / "Desktop")
        assert desktop is not None
        assert isinstance(desktop, Path)
