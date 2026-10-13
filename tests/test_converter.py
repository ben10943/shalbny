"""
Unit tests for Shalbny conversion engine.
Tests bidirectional conversion, ligatures, shifted keys, and edge cases.
"""
import pytest
from src.converter.arabic_english import ArabicEnglishProfile
from src.converter.manager import ProfileManager


class TestArabicEnglishConverter:

    @pytest.fixture
    def profile(self):
        return ArabicEnglishProfile()

    def test_english_to_arabic_words(self, profile):
        # 'fdv,j' -> 'بيروت'
        assert profile.convert("fdv,j") == "بيروت"
        # 'lpl]' -> 'محمد'
        assert profile.convert("lpl]") == "محمد"
        # 'lk' -> 'من'
        assert profile.convert("lk") == "من"
        # 'hgsghl ugd;l' -> 'السلام عليكم'
        assert profile.convert("hgsghl ugd;l") == "السلام عليكم"

    def test_arabic_to_english_words(self, profile):
        # 'اثممخ' -> 'hello'
        assert profile.convert("اثممخ") == "hello"
        # 'صخقمي' -> 'world'
        assert profile.convert("صخقمي") == "world"
        # 'فثسف' -> 'test'
        assert profile.convert("فثسف") == "test"
        # 'حغفاخى' -> 'python'
        assert profile.convert("حغفاخى") == "python"

    def test_ligatures_b_to_la(self, profile):
        # 'b' in English keyboard corresponds to 'لا' in Arabic keyboard
        assert profile.convert("b") == "لا"
        assert profile.convert("لا") == "b"

        # 'B' in English keyboard corresponds to 'لآ'
        assert profile.convert("B") == "لآ"
        assert profile.convert("لآ") == "B"

        # 'T' (Shift+t) -> 'لإ'
        assert profile.convert("T") == "لإ"
        assert profile.convert("لإ") == "T"

        # 'G' (Shift+g) -> 'لأ'
        assert profile.convert("G") == "لأ"
        assert profile.convert("لأ") == "G"

    def test_tashkeel_and_shifted_keys(self, profile):
        # 'Q' -> 'َ' (fatha)
        assert profile.convert("Q") == "َ"
        assert profile.convert("َ") == "Q"

        # 'W' -> 'ً' (tanwin fath)
        assert profile.convert("W") == "ً"
        assert profile.convert("ً") == "W"

        # 'X' -> 'ْ' (sukun)
        assert profile.convert("X") == "ْ"
        assert profile.convert("ْ") == "X"

        # '?' -> '؟'
        assert profile.convert("?") == "؟"
        assert profile.convert("؟") == "?"

        # 'K' (Shift+k) -> '،' (arabic comma)
        assert profile.convert("K") == "،"
        assert profile.convert("،") == "K"

    def test_full_sentences(self, profile):
        sentence_en_typed = "hkh hpf fvl[m hg;lfd,jv"
        expected_ar = "انا احب برمجة الكمبيوتر"
        assert profile.convert(sentence_en_typed) == expected_ar

        # Reverse
        assert profile.convert(expected_ar) == sentence_en_typed

    def test_mixed_or_empty_text(self, profile):
        assert profile.convert("") == ""
        assert profile.convert("   ") == "   "
        assert profile.convert("123 456") == "123 456"

    def test_profile_manager(self):
        manager = ProfileManager()
        assert manager.active_profile.id == "ar_en"
        assert len(manager.list_profiles()) >= 1
        assert manager.convert("اثممخ") == "hello"
