import os
import json
import tempfile
from unittest.mock import patch, mock_open
from app.config import Config, get_logs, log, LOG_FILE


class TestConfig:
    def setup_method(self):
        self.test_dir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.test_dir, "config.json")

    @patch("app.config.CONFIG_FILE", new_callable=lambda: None)
    @patch("app.config.os.makedirs")
    @patch("app.config.os.path.exists", return_value=False)
    def test_default_values(self, mock_exists, mock_mkdir, mock_cfg_file):
        c = Config()
        assert c.get("monitoring_interval") == 1000
        assert c.get("plugins_enabled") is True
        assert c.get("nonexistent", "fallback") == "fallback"

    @patch("app.config.CONFIG_FILE", new_callable=lambda: None)
    @patch("app.config.os.makedirs")
    @patch("builtins.open", new_callable=mock_open, read_data='{"monitoring_interval": 5000, "theme": "Light"}')
    @patch("app.config.os.path.exists", return_value=True)
    def test_loads_saved_config(self, mock_exists, mock_open_file, mock_mkdir, mock_cfg_file):
        c = Config()
        assert c.get("monitoring_interval") == 5000
        assert c.get("theme") == "Light"
        assert c.get("plugins_enabled") is True

    @patch("app.config.CONFIG_FILE", new_callable=lambda: None)
    @patch("app.config.os.makedirs")
    @patch("app.config.os.path.exists", return_value=False)
    def test_get_all_returns_copy(self, mock_exists, mock_mkdir, mock_cfg_file):
        c = Config()
        all_data = c.get_all()
        assert isinstance(all_data, dict)
        assert "monitoring_interval" in all_data
        all_data["test"] = "value"
        assert c.get("test") is None


class TestLogFunctions:
    @patch("builtins.open", new_callable=mock_open)
    @patch("app.config.LOG_FILE", "test_log.txt")
    def test_log_writes_entry(self, mock_file):
        log("Test entry")
        mock_file().write.assert_called()

    @patch("builtins.open", side_effect=PermissionError)
    @patch("app.config.LOG_FILE", "test_log.txt")
    def test_log_handles_permission_error(self, mock_file):
        log("This should not crash")
        assert True

    @patch("builtins.open", new_callable=mock_open, read_data="[2024-01-01] Hello\n[2024-01-02] World\n")
    @patch("app.config.os.path.exists", return_value=True)
    def test_get_logs_returns_content(self, mock_exists, mock_file):
        content = get_logs()
        assert "Hello" in content
        assert "World" in content

    @patch("app.config.os.path.exists", return_value=False)
    def test_get_logs_no_file(self, mock_exists):
        assert get_logs() == ""
