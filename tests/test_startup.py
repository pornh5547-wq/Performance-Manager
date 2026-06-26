from unittest.mock import patch, MagicMock
from app.utils.startup import StartupManager


SAMPLE_WMI_JSON = r"""[
    {"Name": "OneDrive", "Command": "C:/Program Files/OneDrive/OneDrive.exe", "Location": "HKLM/Software/Microsoft/Windows/CurrentVersion/Run", "User": "Public"},
    {"Name": "Steam", "Command": "C:/Program Files (x86)/Steam/steam.exe", "Location": "HKCU/Software/Microsoft/Windows/CurrentVersion/Run", "User": "User"}
]"""

SAMPLE_REG_JSON = r'{"PSPath": "foo", "PSParentPath": "bar", "OneDrive": "C:/Program Files/OneDrive/OneDrive.exe", "": "", "Steam": "C:/Program Files (x86)/Steam/steam.exe"}'


class TestStartupManager:
    def setup_method(self):
        self.manager = StartupManager()

    @patch("app.utils.startup._run_pwsh")
    def test_get_startup_items_from_wmi(self, mock_run):
        mock_run.return_value = MagicMock(stdout=SAMPLE_WMI_JSON, returncode=0)
        items = self.manager.get_startup_items()
        assert len(items) >= 2
        names = [i["name"] for i in items]
        assert "OneDrive" in names
        assert "Steam" in names

    @patch("app.utils.startup._run_pwsh", return_value=None)
    def test_handles_none_result(self, mock_run):
        items = self.manager.get_startup_items()
        assert items == []

    @patch("app.utils.startup._run_pwsh")
    def test_disable_startup_item_hklm(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        assert self.manager.disable_startup_item("TestApp", "HKLM") is True
        call_args = mock_run.call_args[0][0]
        assert "Remove-ItemProperty" in call_args
        assert "HKLM:" in call_args

    @patch("app.utils.startup._run_pwsh")
    def test_disable_startup_item_hkcu(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        assert self.manager.disable_startup_item("TestApp", "HKCU") is True
        call_args = mock_run.call_args[0][0]
        assert "HKCU:" in call_args

    @patch("app.utils.startup._run_pwsh", return_value=None)
    def test_disable_failure(self, mock_run):
        assert self.manager.disable_startup_item("TestApp", "HKCU") is False

    @patch("app.utils.startup._run_pwsh")
    def test_enable_startup_item(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        assert self.manager.enable_startup_item("TestApp", "C:\\test.exe", "HKCU") is True
        call_args = mock_run.call_args[0][0]
        assert "Set-ItemProperty" in call_args
        assert "C:\\test.exe" in call_args
