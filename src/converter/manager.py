"""
Language Profile Manager for Shalbny.
Provides profile registry and dynamic resolution for multi-language extensibility.
"""
from typing import Dict, List, Optional
from .base import LanguageProfile
from .arabic_english import ArabicEnglishProfile


class ProfileManager:
    """Manages registered language profiles."""

    def __init__(self):
        self._profiles: Dict[str, LanguageProfile] = {}
        # Register default built-in profile
        self.register(ArabicEnglishProfile())
        self._active_profile_id = "ar_en"

    def register(self, profile: LanguageProfile) -> None:
        """Register a new language profile."""
        self._profiles[profile.id] = profile

    def get_profile(self, profile_id: str) -> Optional[LanguageProfile]:
        """Get profile by unique identifier."""
        return self._profiles.get(profile_id)

    def list_profiles(self) -> List[LanguageProfile]:
        """List all registered profiles."""
        return list(self._profiles.values())

    @property
    def active_profile(self) -> LanguageProfile:
        """Get the currently active profile."""
        profile = self._profiles.get(self._active_profile_id)
        if not profile:
            # Fallback to first available
            return next(iter(self._profiles.values()))
        return profile

    def set_active_profile(self, profile_id: str) -> bool:
        """Set active profile by id."""
        if profile_id in self._profiles:
            self._active_profile_id = profile_id
            return True
        return False

    def convert(self, text: str, profile_id: Optional[str] = None) -> str:
        """Convert text using specified profile or active profile."""
        profile = self.get_profile(profile_id) if profile_id else self.active_profile
        if not profile:
            return text
        return profile.convert(text)
