from unittest.mock import patch, MagicMock
from app.utils.admin import (
    run_dism_command, run_sfc_command, run_chkdsk_command,
    run_ipconfig_command, create_restore_point,
    enable_gaming_mode, disable_gaming_mode,
    enable_windows_updates, disable_windows_updates,
    set_high_performance_power_plan, clear_dns_cache,
    reset_winsock, reset_ip_stack, get_windows_health,
)


class TestAdminCommands:
    @patch("app.utils.admin.run_admin")
    def test_run_dism_command(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        r = run_dism_command("ScanHealth")
        assert r is not None
        call = mock_run_admin.call_args[0][0]
        assert "DISM" in call and "ScanHealth" in call

    @patch("app.utils.admin.run_admin")
    def test_run_sfc_command(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        r = run_sfc_command()
        assert r is not None
        assert "sfc /scannow" in mock_run_admin.call_args[0][0]

    @patch("app.utils.admin.run_admin")
    def test_run_chkdsk_command(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        r = run_chkdsk_command("D:")
        assert r is not None
        assert "chkdsk D:" in mock_run_admin.call_args[0][0]

    @patch("app.utils.admin.run")
    def test_run_ipconfig_command(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="Windows IP Configuration\n")
        r = run_ipconfig_command("/all")
        assert r is not None
        assert "ipconfig /all" in mock_run.call_args[0][0]

    @patch("app.utils.admin.run_admin")
    def test_create_restore_point(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        r = create_restore_point("Test point")
        assert r is not None
        assert "Checkpoint-Computer" in mock_run_admin.call_args[0][0]

    @patch("app.utils.admin.run_admin")
    def test_enable_gaming_mode(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert enable_gaming_mode() is not None

    @patch("app.utils.admin.run_admin")
    def test_disable_gaming_mode(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert disable_gaming_mode() is not None

    @patch("app.utils.admin.run_admin")
    def test_enable_windows_updates(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert enable_windows_updates() is not None

    @patch("app.utils.admin.run_admin")
    def test_disable_windows_updates(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert disable_windows_updates() is not None

    @patch("app.utils.admin.run_admin")
    def test_set_high_performance_power_plan(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert set_high_performance_power_plan() is not None
        assert "powercfg" in mock_run_admin.call_args[0][0]

    @patch("app.utils.admin.run_admin")
    def test_clear_dns_cache(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert clear_dns_cache() is not None
        assert "ipconfig /flushdns" in mock_run_admin.call_args[0][0]

    @patch("app.utils.admin.run_admin")
    def test_reset_winsock(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert reset_winsock() is not None
        assert "netsh winsock reset" in mock_run_admin.call_args[0][0]

    @patch("app.utils.admin.run_admin")
    def test_reset_ip_stack(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert reset_ip_stack() is not None
        assert "netsh int ip reset" in mock_run_admin.call_args[0][0]


class TestGetWindowsHealth:
    @patch("app.utils.admin.run")
    def test_healthy(self, mock_run):
        mock_run.side_effect = [
            MagicMock(stdout="No component store corruption detected", returncode=0),
            MagicMock(stdout="did not find any integrity violations", returncode=0),
        ]
        health = get_windows_health()
        assert health["dism_health"] == "Healthy"
        assert health["sfc_status"] == "Healthy"

    @patch("app.utils.admin.run")
    def test_repairable(self, mock_run):
        mock_run.side_effect = [
            MagicMock(stdout="The component store is repairable", returncode=0),
            MagicMock(stdout="corruption found", returncode=0),
        ]
        health = get_windows_health()
        assert health["dism_health"] == "Repairable"
        assert health["sfc_status"] == "Corruption Found"

    @patch("app.utils.admin.run")
    def test_unknown_on_none(self, mock_run):
        mock_run.return_value = None
        health = get_windows_health()
        assert health["dism_health"] == "Unknown"
        assert health["sfc_status"] == "Unknown"

    @patch("app.utils.admin.run")
    def test_unknown_on_empty_stdout(self, mock_run):
        mock_run.return_value = MagicMock(stdout="", returncode=0)
        health = get_windows_health()
        assert health["dism_health"] == "Unknown"
        assert health["sfc_status"] == "Unknown"
