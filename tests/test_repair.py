import time
from unittest.mock import patch, MagicMock
from app.utils.repair import WindowsRepair, NetworkRepair


class TestWindowsRepair:
    @patch("app.utils.repair.run_admin")
    def test_run_dism_scan(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
        callback = MagicMock()
        WindowsRepair.run_dism_scan(callback=callback)
        time.sleep(0.1)
        callback.assert_called_once()
        args = callback.call_args[0]
        assert args[0] == "dism_scan"
        assert args[1] is True
        assert "ok" in args[2]

    @patch("app.utils.repair.run_admin")
    def test_run_dism_restore(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0, stdout="restored", stderr="")
        callback = MagicMock()
        WindowsRepair.run_dism_restore(callback=callback)
        time.sleep(0.1)
        callback.assert_called_once()
        assert callback.call_args[0][0] == "dism_restore"

    @patch("app.utils.repair.run_admin")
    def test_run_sfc_scan(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
        callback = MagicMock()
        WindowsRepair.run_sfc_scan(callback=callback)
        time.sleep(0.1)
        callback.assert_called_once()
        assert callback.call_args[0][0] == "sfc"

    @patch("app.utils.repair.run_admin")
    def test_run_chkdsk(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0, stdout="ok", stderr="")
        callback = MagicMock()
        WindowsRepair.run_chkdsk("D:", callback=callback)
        time.sleep(0.1)
        callback.assert_called_once()
        assert callback.call_args[0][0] == "chkdsk"
        assert "D:" in mock_run_admin.call_args[0][0]

    @patch("app.utils.repair.run_admin", return_value=None)
    def test_failure_sets_ok_false(self, mock_run_admin):
        callback = MagicMock()
        WindowsRepair.run_dism_scan(callback=callback)
        time.sleep(0.1)
        callback.assert_called_once()
        assert callback.call_args[0][1] is False

    @patch("app.utils.repair.run_admin")
    def test_chkdsk_no_callback(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        WindowsRepair.run_dism_scan()
        time.sleep(0.1)


class TestNetworkRepair:
    @patch("app.utils.repair.run_admin")
    def test_flush_dns(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        callback = MagicMock()
        NetworkRepair.flush_dns(callback=callback)
        time.sleep(0.1)
        callback.assert_called_once_with("dns_flush", True, "")

    @patch("app.utils.repair.run_admin")
    def test_reset_winsock(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        callback = MagicMock()
        NetworkRepair.reset_winsock(callback=callback)
        time.sleep(0.1)
        callback.assert_called_once_with("winsock", True, "")

    @patch("app.utils.repair.run_admin")
    def test_reset_ip(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        callback = MagicMock()
        NetworkRepair.reset_ip(callback=callback)
        time.sleep(0.1)
        callback.assert_called_once_with("ip_reset", True, "")

    @patch("app.utils.repair.run_admin")
    def test_renew_ip(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        callback = MagicMock()
        NetworkRepair.renew_ip(callback=callback)
        time.sleep(0.1)
        callback.assert_called_once_with("ip_renew", True, "")

    @patch("app.utils.repair.run_admin")
    def test_reset_all(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        callback = MagicMock()
        NetworkRepair.reset_all(callback=callback)
        time.sleep(0.1)
        callback.assert_called_once()
        assert callback.call_args[0][0] == "network_reset_all"
        assert callback.call_args[0][1] is True

    @patch("app.utils.repair.run_admin")
    def test_no_callback(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        NetworkRepair.flush_dns()
        NetworkRepair.reset_winsock()
        NetworkRepair.reset_ip()
        NetworkRepair.renew_ip()
        NetworkRepair.reset_all()
