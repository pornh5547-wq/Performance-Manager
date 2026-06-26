from unittest.mock import patch, MagicMock
from app.utils.battery import get_battery_info, get_power_scheme, generate_battery_report, get_battery_history


class TestGetBatteryInfo:
    @patch("app.utils.battery.run")
    def test_returns_battery_info(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout='{"Name": "Test Battery", "EstimatedChargeRemaining": 85, "BatteryStatus": 2}',
            returncode=0
        )
        info = get_battery_info()
        assert info["Name"] == "Test Battery"
        assert info["EstimatedChargeRemaining"] == 85

    @patch("app.utils.battery.run", return_value=None)
    def test_handles_none(self, mock_run):
        info = get_battery_info()
        assert info == {}

    @patch("app.utils.battery.run", return_value=MagicMock(stdout="invalid", returncode=0))
    def test_invalid_json(self, mock_run):
        info = get_battery_info()
        assert info == {}


class TestGetPowerScheme:
    @patch("app.utils.battery.run")
    def test_high_performance(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="Power Scheme: {8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c} (High performance)",
            returncode=0
        )
        assert get_power_scheme() == "High Performance"

    @patch("app.utils.battery.run")
    def test_balanced(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="Power Scheme: {381b4222-f694-41f0-9685-ff5bb260df2e} (Balanced)",
            returncode=0
        )
        assert get_power_scheme() == "Balanced"

    @patch("app.utils.battery.run")
    def test_power_saver(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="Power Scheme: {a1841308-3541-4fab-bc81-f71556f20b4a} (Power saver)",
            returncode=0
        )
        assert get_power_scheme() == "Power Saver"

    @patch("app.utils.battery.run", return_value=None)
    def test_unknown(self, mock_run):
        assert get_power_scheme() == "Unknown"


class TestGenerateBatteryReport:
    @patch("subprocess.run")
    @patch("os.path.exists", return_value=True)
    @patch("os.makedirs")
    def test_success(self, mock_mkdir, mock_exists, mock_run):
        result = generate_battery_report()
        assert result["success"] is True
        assert "path" in result

    @patch("subprocess.run", side_effect=Exception("boom"))
    @patch("os.makedirs")
    def test_failure(self, mock_mkdir, mock_run):
        result = generate_battery_report()
        assert result["success"] is False


class TestGetBatteryHistory:
    @patch("os.path.exists", return_value=True)
    def test_report_exists(self, mock_exists):
        result = get_battery_history()
        assert result["exists"] is True
        assert "report_path" in result

    @patch("os.path.exists", return_value=False)
    def test_no_report(self, mock_exists):
        result = get_battery_history()
        assert result["exists"] is False
