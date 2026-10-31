"""
Update checker service for Shalbny.
Fetches the latest official GitHub Release and compares it with the local
APP_VERSION using the standard library only (zero new dependencies).
"""
import json
try:
    import urllib.request
    import urllib.error
    HAS_NETWORKING = True
except (ImportError, Exception):
    urllib = None
    HAS_NETWORKING = False
from typing import Dict, Optional

from ..version import (
    APP_VERSION,
    RELEASES_API_URL,
    RELEASES_PAGE_URL,
    compare_versions,
)

REQUEST_HEADERS = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "Shalbny-Updater",
}


def fetch_latest_release(timeout: float = 5.0, api_url: str = RELEASES_API_URL) -> Optional[Dict]:
    """
    Fetches the latest GitHub release metadata.
    Returns a dict with tag_name / html_url / name, or None on any failure.
    """
    if not HAS_NETWORKING or urllib is None:
        return None
    try:
        request = urllib.request.Request(api_url, headers=REQUEST_HEADERS)
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
        if isinstance(payload, dict) and payload.get("tag_name"):
            return payload
        return None
    except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError):
        return None


def check_for_updates(api_url: str = RELEASES_API_URL, timeout: float = 5.0) -> Dict:
    """
    Compares the local version against the latest published GitHub release.
    Returns a result dictionary:
        {"status": "update_available", "latest_version": ..., "current_version": ...,
         "download_page": ..., "release_name": ...}
        {"status": "up_to_date", "current_version": ...}
        {"status": "error", "error": ...}
    """
    release = fetch_latest_release(timeout=timeout, api_url=api_url)
    if not release:
        return {"status": "error", "error": "unreachable"}

    latest_raw = str(release.get("tag_name", "")).strip()
    latest = latest_raw.lstrip("vV") or latest_raw

    relation = compare_versions(latest, APP_VERSION)
    if relation > 0:
        return {
            "status": "update_available",
            "current_version": APP_VERSION,
            "latest_version": latest,
            "download_page": release.get("html_url") or RELEASES_PAGE_URL,
            "release_name": release.get("name") or latest_raw,
        }
    return {"status": "up_to_date", "current_version": APP_VERSION}
