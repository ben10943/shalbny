"""
Central version registry for Shalbny.
Single source of truth for the app version and official release endpoints.
"""

APP_VERSION = "1.2.0"
APP_VERSION_TAG = "v1.2.0"

GITHUB_REPO = "ben10943/shalbny"
RELEASES_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
RELEASES_PAGE_URL = f"https://github.com/{GITHUB_REPO}/releases"


def compare_versions(candidate: str, current: str) -> int:
    """
    Numeric-safe version comparison ("1.10.0" vs "1.9.0" works correctly).
    Returns:
         1 -> candidate is newer
         0 -> identical versions
        -1 -> candidate is older
    """
    try:
        def _parse(ver: str):
            clean = ver.strip().lstrip("vV")
            parts = []
            for chunk in clean.replace("-", ".").split("."):
                digits = ""
                for ch in chunk:
                    if ch.isdigit():
                        digits += ch
                    else:
                        break
                parts.append(int(digits) if digits else 0)
            while len(parts) < 3:
                parts.append(0)
            return parts[:3]

        cand = _parse(candidate)
        curr = _parse(current)
        if cand > curr:
            return 1
        if cand < curr:
            return -1
        return 0
    except Exception:
        return 0
