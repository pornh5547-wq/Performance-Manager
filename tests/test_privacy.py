from unittest.mock import patch, MagicMock
from app.utils.privacy import get_privacy_status, block_telemetry, unblock_telemetry, TELEMETRY_DOMAINS


class TestGetPrivacyStatus:
    @patch("app.utils.privacy.run")
    @patch("app.utils.privacy.os.path.exists", return_value=True)
    @patch("app.utils.privacy.os.environ.get", return_value="C:\\Users\\test\\AppData\\Local")
    def test_returns_status(self, mock_env, mock_exists, mock_run):
        mock_run.side_effect = [
            MagicMock(stdout="Running\n", returncode=0),
            MagicMock(stdout="Stopped\n", returncode=0),
            MagicMock(stdout="0\n", returncode=0),
        ]
        status = get_privacy_status()
        assert "telemetry_service" in status
        assert "push_service" in status
        assert "telemetry_level" in status
        assert "hosts_blocked" in status

    @patch("app.utils.privacy.run", side_effect=Exception("boom"))
    def test_handles_exceptions(self, mock_run):
        status = get_privacy_status()
        assert status.get("telemetry_service") == "Unknown"


class TestTelemetryDomains:
    def test_has_domains(self):
        assert len(TELEMETRY_DOMAINS) > 10
        assert "vortex.data.microsoft.com" in TELEMETRY_DOMAINS
        assert "telemetry.microsoft.com" in TELEMETRY_DOMAINS


class TestBlockTelemetry:
    @patch("app.utils.privacy.run_admin")
    @patch("app.utils.privacy.os.path.exists", return_value=False)
    @patch("app.utils.privacy.open", new_callable=MagicMock)
    @patch("app.utils.privacy._block_telemetry_hosts", return_value=True)
    def test_block_telemetry(self, mock_block_hosts, mock_open_file, mock_exists, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0, stdout="")
        results = block_telemetry()
        assert len(results) > 0
        for item, status in results:
            assert status != "Error"

    @patch("app.utils.privacy.run_admin", return_value=None)
    def test_block_telemetry_all_fail(self, mock_run_admin):
        results = block_telemetry()
        for item, status in results:
            if item != "Telemetry Hosts":
                assert "Failed" in status or status == "Error"


class TestUnblockTelemetry:
    @patch("app.utils.privacy.run_admin")
    @patch("app.utils.privacy.os.path.exists", return_value=False)
    @patch("app.utils.privacy._remove_telemetry_hosts")
    def test_unblock_telemetry(self, mock_remove_hosts, mock_exists, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0, stdout="")
        results = unblock_telemetry()
        assert len(results) > 0

    @patch("app.utils.privacy.run_admin", return_value=None)
    @patch("app.utils.privacy._remove_telemetry_hosts")
    def test_unblock_telemetry_failures(self, mock_remove_hosts, mock_run_admin):
        results = unblock_telemetry()
        for item, status in results:
            if item not in ("Telemetry Hosts",):
                assert "Failed" in status or status == "Error"
