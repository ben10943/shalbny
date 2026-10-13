"""
Arabic (Windows 101) <-> English (QWERTY) layout conversion profile.
Handles lower/uppercase (Shift layer), diacritics (tashkeel), and ligatures (lam-alif).
"""
import re
from .base import LanguageProfile


class ArabicEnglishProfile(LanguageProfile):
    """Bidirectional converter between English QWERTY and Arabic 101 layout."""

    # English -> Arabic mapping (Direct single key)
    EN_TO_AR = {
        # Lowercase / Normal
        '`': 'ذ', 'q': 'ض', 'w': 'ص', 'e': 'ث', 'r': 'ق', 't': 'ف', 'y': 'غ',
        'u': 'ع', 'i': 'ه', 'o': 'خ', 'p': 'ح', '[': 'ج', ']': 'د',
        'a': 'ش', 's': 'س', 'd': 'ي', 'f': 'ب', 'g': 'ل', 'h': 'ا',
        'j': 'ت', 'k': 'ن', 'l': 'م', ';': 'ك', "'": 'ط',
        'z': 'ئ', 'x': 'ء', 'c': 'ؤ', 'v': 'ر', 'b': 'لا', 'n': 'ى',
        'm': 'ة', ',': 'و', '.': 'ز', '/': 'ظ',

        # Shifted / Uppercase
        '~': 'ّ', 'Q': 'َ', 'W': 'ً', 'E': 'ُ', 'R': 'ٌ', 'T': 'لإ', 'Y': 'إ',
        'U': '‘', 'I': '÷', 'O': '×', 'P': '؛', '{': '<', '}': '>',
        'A': 'ِ', 'S': 'ٍ', 'D': ']', 'F': '[', 'G': 'لأ', 'H': 'أ',
        'J': 'ـ', 'K': '،', 'L': '/', ':': ':', '"': '"',
        'Z': '~', 'X': 'ْ', 'C': '}', 'V': '{', 'B': 'لآ', 'N': 'آ',
        'M': '’', '<': ',', '>': '.', '?': '؟'
    }

    # Arabic -> English mapping
    AR_TO_EN = {
        'ذ': '`', 'ض': 'q', 'ص': 'w', 'ث': 'e', 'ق': 'r', 'ف': 't', 'غ': 'y',
        'ع': 'u', 'ه': 'i', 'خ': 'o', 'ح': 'p', 'ج': '[', 'د': ']',
        'ش': 'a', 'س': 's', 'ي': 'd', 'ب': 'f', 'ل': 'g', 'ا': 'h',
        'ت': 'j', 'ن': 'k', 'م': 'l', 'ك': ';', 'ط': "'",
        'ئ': 'z', 'ء': 'x', 'ؤ': 'c', 'ر': 'v', 'ى': 'n',
        'ة': 'm', 'و': ',', 'ز': '.', 'ظ': '/',

        # Tashkeel & Shifted Arabic
        'ّ': '~', 'َ': 'Q', 'ً': 'W', 'ُ': 'E', 'ٌ': 'R', 'إ': 'Y',
        '‘': 'U', '÷': 'I', '×': 'O', '؛': 'P',
        'ِ': 'A', 'ٍ': 'S', 'أ': 'H', 'ـ': 'J', '،': 'K',
        'ْ': 'X', 'آ': 'N', '’': 'M', '؟': '?'
    }

    # Multi-character ligatures (Arabic -> English)
    # Check these first in Arabic strings
    LIGATURES_AR_TO_EN = [
        ('لآ', 'B'),
        ('لأ', 'G'),
        ('لإ', 'T'),
        ('لا', 'b'),
        ('\uFEF5', 'B'),  # Arabic Ligature Lam with Alef with Madda Above Isolated Form
        ('\uFEF6', 'B'),
        ('\uFEF7', 'G'),  # Arabic Ligature Lam with Alef with Hamza Above Isolated Form
        ('\uFEF8', 'G'),
        ('\uFEF9', 'T'),  # Arabic Ligature Lam with Alef with Hamza Below Isolated Form
        ('\uFEFA', 'T'),
        ('\uFEFB', 'b'),  # Arabic Ligature Lam with Alef Isolated Form
        ('\uFEFC', 'b')
    ]

    @property
    def id(self) -> str:
        return "ar_en"

    @property
    def display_name(self) -> str:
        return "عربي ⟷ English (Arabic 101 / QWERTY)"

    def can_handle(self, text: str) -> bool:
        """Determines if the text contains any recognizable Arabic or English characters."""
        if not text:
            return False
        for char in text:
            if char in self.EN_TO_AR or char in self.AR_TO_EN:
                return True
        return False

    def detect_direction(self, text: str) -> str:
        """
        Detects primary language direction: 'to_arabic' or 'to_english'.
        Counts Arabic vs English characters.
        """
        arabic_count = 0
        english_count = 0

        for char in text:
            # Arabic unicode ranges
            if ('\u0600' <= char <= '\u06FF') or ('\uFB50' <= char <= '\uFEFC') or char in self.AR_TO_EN:
                arabic_count += 1
            # English letters
            elif ('a' <= char <= 'z') or ('A' <= char <= 'Z'):
                english_count += 1
            elif char in self.EN_TO_AR and char not in self.AR_TO_EN:
                # Key is unique to english layout
                english_count += 1

        if arabic_count > english_count:
            return 'to_english'
        if english_count > arabic_count:
            return 'to_arabic'

        # Fallback for symbol-heavy text (e.g. '؟' vs '?')
        if any(c in '،؛؟' for c in text):
            return 'to_english'
        if any(c in '?~`' for c in text):
            return 'to_arabic'

        return 'to_arabic'

    def to_arabic(self, text: str) -> str:
        """Converts English QWERTY characters to Arabic 101."""
        result = []
        for char in text:
            result.append(self.EN_TO_AR.get(char, char))
        return "".join(result)

    def to_english(self, text: str) -> str:
        """Converts Arabic 101 characters to English QWERTY, respecting ligatures."""
        # First handle multi-character ligatures
        processed = text
        for ar_lig, en_char in self.LIGATURES_AR_TO_EN:
            processed = processed.replace(ar_lig, en_char)

        # Then translate character by character
        result = []
        for char in processed:
            result.append(self.AR_TO_EN.get(char, char))
        return "".join(result)

    def convert(self, text: str) -> str:
        """Automatically detects direction and converts the text."""
        if not text:
            return ""

        direction = self.detect_direction(text)
        if direction == 'to_english':
            return self.to_english(text)
        else:
            return self.to_arabic(text)
