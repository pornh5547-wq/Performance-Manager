from unittest.mock import patch, MagicMock
from app.utils.ssd_optimizer import SSDOptimizer


class TestCheckTrimStatus:
    @patch("app.utils.ssd_optimizer.run")
    def test_trim_enabled(self, mock_run):
        mock_run.return_value = MagicMock(stdout="DisableDeleteNotify = 0", returncode=0)
        result = SSDOptimizer.check_trim_status()
        assert result["trim_enabled"] is True

    @patch("app.utils.ssd_optimizer.run")
    def test_trim_disabled(self, mock_run):
        mock_run.return_value = MagicMock(stdout="DisableDeleteNotify = 1", returncode=0)
        result = SSDOptimizer.check_trim_status()
        assert result["trim_enabled"] is False

    @patch("app.utils.ssd_optimizer.run", return_value=None)
    def test_trim_unknown(self, mock_run):
        result = SSDOptimizer.check_trim_status()
        assert result["trim_enabled"] is None

    @patch("app.utils.ssd_optimizer.run")
    def test_trim_unknown_on_unexpected(self, mock_run):
        mock_run.return_value = MagicMock(stdout="unexpected output", returncode=0)
        result = SSDOptimizer.check_trim_status()
        assert result["trim_enabled"] is None

    @patch("app.utils.ssd_optimizer.run", return_value=MagicMock(stdout="", returncode=0))
    def test_trim_unknown_on_empty(self, mock_run):
        result = SSDOptimizer.check_trim_status()
        assert result["trim_enabled"] is None


class TestEnableTrim:
    @patch("app.utils.ssd_optimizer.run_admin")
    def test_enable_trim_success(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        result = SSDOptimizer.enable_trim()
        assert result["success"] is True

    @patch("app.utils.ssd_optimizer.run_admin", return_value=None)
    def test_enable_trim_failure(self, mock_run_admin):
        result = SSDOptimizer.enable_trim()
        assert result["success"] is False


class TestOptimizeAllDrives:
    @patch("app.utils.ssd_optimizer.run_admin")
    def test_optimize_success(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0, stdout="ok")
        result = SSDOptimizer.optimize_all_drives()
        assert result["success"] is True
        assert result["output"] == "ok"

    @patch("app.utils.ssd_optimizer.run_admin", return_value=None)
    def test_optimize_failure(self, mock_run_admin):
        result = SSDOptimizer.optimize_all_drives()
        assert result["success"] is False


class TestGetDriveInfo:
    @patch("app.utils.ssd_optimizer.run")
    def test_returns_parsed_json(self, mock_run):
        mock_run.return_value = MagicMock(stdout='{"Model": "Samsung SSD"}', returncode=0)
        result = SSDOptimizer.get_drive_info("C:")
        assert result.get("Model") == "Samsung SSD"

    @patch("app.utils.ssd_optimizer.run")
    def test_returns_empty_on_invalid(self, mock_run):
        mock_run.return_value = MagicMock(stdout="not json", returncode=0)
        result = SSDOptimizer.get_drive_info("C:")
        assert result == {}

    @patch("app.utils.ssd_optimizer.run", return_value=None)
    def test_returns_empty_on_none(self, mock_run):
        result = SSDOptimizer.get_drive_info("C:")
        assert result == {}


class TestDisableSysmain:
    @patch("app.utils.ssd_optimizer.run_admin")
    def test_disable_sysmain_success(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        result = SSDOptimizer.disable_sysmain()
        assert result["success"] is True

    @patch("app.utils.ssd_optimizer.run_admin", return_value=None)
    def test_disable_sysmain_failure(self, mock_run_admin):
        result = SSDOptimizer.disable_sysmain()
        assert result["success"] is False


class TestRunFullOptimization:
    @patch("app.utils.ssd_optimizer.SSDOptimizer.check_trim_status")
    @patch("app.utils.ssd_optimizer.SSDOptimizer.optimize_all_drives")
    @patch("app.utils.ssd_optimizer.SSDOptimizer.disable_sysmain")
    @patch("app.utils.ssd_optimizer.SSDOptimizer.enable_trim")
    def test_full_optimization_trim_enabled(self, enable, sysmain, optimize, trim):
        trim.return_value = {"trim_enabled": True}
        optimize.return_value = {"success": True}
        sysmain.return_value = {"success": True}
        result = SSDOptimizer.run_full_optimization()
        assert result["trim"]["trim_enabled"] is True
        enable.assert_not_called()

    @patch("app.utils.ssd_optimizer.SSDOptimizer.check_trim_status")
    @patch("app.utils.ssd_optimizer.SSDOptimizer.optimize_all_drives")
    @patch("app.utils.ssd_optimizer.SSDOptimizer.disable_sysmain")
    @patch("app.utils.ssd_optimizer.SSDOptimizer.enable_trim")
    def test_full_optimization_trim_disabled(self, enable, sysmain, optimize, trim):
        trim.return_value = {"trim_enabled": False}
        optimize.return_value = {"success": True}
        sysmain.return_value = {"success": True}
        result = SSDOptimizer.run_full_optimization()
        assert result["trim"]["trim_enabled"] is False
        enable.assert_called_once()
