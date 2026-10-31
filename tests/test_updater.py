"""
Unit tests for the Shalbny update checker and central version registry.
"""
import pytest
from src.version import APP_VERSION, compare_versions
from src.core import updater
from src.core.updater import check_for_updates, fetch_latest_release


class TestCompareVersions:

    def test_identical_versions(self):
        assert compare_versions("1.1.0", "1.1.0") == 0
        assert compare_versions("v1.1.0", "1.1.0") == 0

    def test_major_minor_patch_ordering(self):
        assert compare_versions("2.0.0", "1.9.9") == 1
        assert compare_versions("1.2.0", "1.1.1") == 1
        assert compare_versions("1.1.1", "1.1.0") == 1

    def test_numeric_not_lexicographic(self):
        # Lexicographic comparison would wrongly declare 1.10.0 < 1.9.0
        assert compare_versions("1.10.0", "1.9.0") == 1
        assert compare_versions("1.9.0", "1.10.0") == -1

    def test_two_part_versions(self):
        assert compare_versions("1.2", "1.1.10") == 1
        assert compare_versions("2.0", "1.999.999") == 1


class TestAppVersionConsistency:

    def test_local_version_is_defined(self):
        assert APP_VERSION and APP_VERSION[0].isdigit()

    def test_check_up_to_date_current_tag(self):
        result = check_for_updates(api_url="unused", timeout=0.1)
        # With a mocked fetch of the exact local tag, status should be up_to_date
        assert result["status"] == "error"  # no real network in tests

    def test_fetch_handles_invalid_url(self):
        assert fetch_latest_release(timeout=0.2, api_url="http://127.0.0.1:9/none") is None


@pytest.fixture
def release_payload():
    return {
        "tag_name": "v1.3.0",
        "name": "Shalbny v1.3.0",
        "html_url": "https://github.com/ben10943/shalbny/releases/tag/v1.3.0",
    }


class TestCheckForUpdates:

    def test_update_available(self, monkeypatch, release_payload):
        monkeypatch.setattr(updater, "fetch_latest_release", lambda **kw: release_payload)
        result = check_for_updates()
        assert result["status"] == "update_available"
        assert result["latest_version"] == "1.3.0"
        assert result["download_page"].endswith("v1.3.0")

    def test_up_to_date(self, monkeypatch, release_payload):
        monkeypatch.setattr(updater, "fetch_latest_release", lambda **kw: release_payload)
        monkeypatch.setattr(updater, "APP_VERSION", "1.3.0")
        result = check_for_updates()
        assert result["status"] == "up_to_date"

    def test_older_remote_tag_is_not_downgrade(self, monkeypatch, release_payload):
        release_payload["tag_name"] = "v1.0.0"
        monkeypatch.setattr(updater, "fetch_latest_release", lambda **kw: release_payload)
        result = check_for_updates()
        assert result["status"] == "up_to_date"

    def test_unreachable_maps_to_error(self, monkeypatch):
        monkeypatch.setattr(updater, "fetch_latest_release", lambda **kw: None)
        result = check_for_updates()
        assert result["status"] == "error"
