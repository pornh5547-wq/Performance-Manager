from unittest.mock import patch, MagicMock
from app.utils.services import list_services, stop_service, start_service, set_startup_type, disable_service, enable_service, SAFE_SERVICES


SAMPLE_SERVICES_JSON = """[
    {"Name": "XblAuthManager", "DisplayName": "Xbox Live Auth Manager", "Status": "Running", "StartType": "Manual", "CanStop": true, "CanPauseAndContinue": false},
    {"Name": "WSearch", "DisplayName": "Windows Search", "Status": "Stopped", "StartType": "Disabled", "CanStop": false, "CanPauseAndContinue": false},
    {"Name": "Dnscache", "DisplayName": "DNS Client", "Status": "Running", "StartType": "Automatic", "CanStop": true, "CanPauseAndContinue": false}
]"""


class TestListServices:
    @patch("app.utils.services.run")
    def test_returns_services_with_safety_badges(self, mock_run):
        mock_run.return_value = MagicMock(stdout=SAMPLE_SERVICES_JSON, returncode=0)
        services = list_services()
        assert len(services) == 3
        xbl = next(s for s in services if s["Name"] == "XblAuthManager")
        assert xbl["Safety"] == "Safe"
        dns = next(s for s in services if s["Name"] == "Dnscache")
        assert dns["Safety"] == "Unknown"

    @patch("app.utils.services.run", return_value=None)
    def test_returns_empty_on_none(self, mock_run):
        assert list_services() == []

    @patch("app.utils.services.run")
    def test_handles_single_dict(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout='{"Name": "TestSvc", "DisplayName": "Test", "Status": "Running", "StartType": "Auto"}',
            returncode=0
        )
        services = list_services()
        assert len(services) == 1
        assert services[0]["Name"] == "TestSvc"

    @patch("app.utils.services.run", return_value=MagicMock(stdout="invalid json", returncode=0))
    def test_invalid_json(self, mock_run):
        assert list_services() == []


class TestSafeServices:
    def test_has_safe_services(self):
        assert "XboxGipSvc" in SAFE_SERVICES
        assert "XblAuthManager" in SAFE_SERVICES
        assert "WSearch" in SAFE_SERVICES
        assert len(SAFE_SERVICES) > 10


class TestServiceActions:
    @patch("app.utils.services.run_admin")
    def test_stop_service(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert stop_service("TestSvc") is True

    @patch("app.utils.services.run_admin")
    def test_start_service(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert start_service("TestSvc") is True

    @patch("app.utils.services.run_admin")
    def test_set_startup_type(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert set_startup_type("TestSvc", "Automatic") is True
        call_args = mock_run_admin.call_args[0][0]
        assert "Set-Service" in call_args
        assert "Automatic" in call_args

    @patch("app.utils.services.run_admin")
    def test_disable_service(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert disable_service("TestSvc") is True
        call_args = mock_run_admin.call_args[0][0]
        assert "Disabled" in call_args
        assert "Stop-Service" in call_args

    @patch("app.utils.services.run_admin")
    def test_enable_service(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert enable_service("TestSvc") is True
        call_args = mock_run_admin.call_args[0][0]
        assert "Manual" in call_args

    @patch("app.utils.services.run_admin", return_value=None)
    def test_returns_false_on_none(self, mock_run_admin):
        assert stop_service("TestSvc") is False
        assert start_service("TestSvc") is False
        assert set_startup_type("TestSvc", "Auto") is False
        assert disable_service("TestSvc") is False
        assert enable_service("TestSvc") is False
