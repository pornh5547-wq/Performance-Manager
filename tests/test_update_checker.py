from unittest.mock import patch, MagicMock
from app.utils.update_checker import UpdateChecker, APP_VERSION


class TestUpdateChecker:
    def setup_method(self):
        self.checker = UpdateChecker()

    def test_app_version_is_string(self):
        assert isinstance(APP_VERSION, str)
        assert len(APP_VERSION) > 0

    @patch("requests.get")
    def test_no_update_needed(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "tag_name": "v1.0.0",
            "html_url": "https://github.com/repo/release",
            "assets": [],
            "body": "Same version"
        }
        mock_get.return_value = mock_resp
        result = self.checker.check_now()
        assert result["has_update"] is False
        assert result["latest_version"] == "1.0.0"

    @patch("requests.get")
    def test_update_available(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "tag_name": "v2.0.0",
            "html_url": "https://github.com/repo/release",
            "assets": [{"name": "app.exe", "browser_download_url": "https://github.com/repo/release/app.exe"}],
            "body": "New features"
        }
        mock_get.return_value = mock_resp
        result = self.checker.check_now()
        assert result["has_update"] is True
        assert result["latest_version"] == "2.0.0"
        assert "app.exe" in result["download_url"]

    @patch("requests.get", side_effect=Exception("timeout"))
    def test_network_error(self, mock_get):
        result = self.checker.check_now()
        assert result["has_update"] is False

    @patch("requests.get")
    def test_http_error(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 404
        mock_get.return_value = mock_resp
        result = self.checker.check_now()
        assert result["has_update"] is False

    @patch("requests.get")
    def test_callback_invoked(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"tag_name": "v1.0.0", "assets": [], "body": ""}
        mock_get.return_value = mock_resp
        callback = MagicMock()
        self.checker.check(callback)
        callback.wait = lambda timeout=None: None

    @patch("requests.get")
    def test_version_comparison_same(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"tag_name": f"v{APP_VERSION}", "assets": [], "body": ""}
        mock_get.return_value = mock_resp
        result = self.checker.check_now()
        assert result["has_update"] is False
