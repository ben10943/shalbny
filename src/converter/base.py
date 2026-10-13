"""
Base Language Profile definition for Shalbny.
Enables pluggable multi-language layout switching.
"""
from abc import ABC, abstractmethod


class LanguageProfile(ABC):
    """Abstract base class for keyboard layout language conversion profiles."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for this profile (e.g. 'ar_en')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable display name (e.g. 'عربي ⟷ English (QWERTY / 101)')."""
        pass

    @abstractmethod
    def convert(self, text: str) -> str:
        """
        Convert the input text across the layout boundaries.
        Automatically detects direction or flips appropriately.
        """
        pass

    @abstractmethod
    def can_handle(self, text: str) -> bool:
        """Check if this profile is capable of handling/detecting the given text."""
        pass
