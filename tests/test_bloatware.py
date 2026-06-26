from unittest.mock import patch, MagicMock
from app.utils.bloatware import list_installed_bloatware, uninstall_package, BLOATWARE_LIST


SAMPLE_PACKAGES_JSON = r"""[
    {"Name": "Microsoft.BingWeather", "PackageFullName": "Microsoft.BingWeather_8wekyb3d8bbwe", "InstallLocation": "C:/Program Files/WindowsApps"},
    {"Name": "Microsoft.SkypeApp", "PackageFullName": "Microsoft.SkypeApp_15.0.0_8wekyb3d8bbwe", "InstallLocation": ""},
    {"Name": "SomeOtherApp", "PackageFullName": "SomeOtherApp_1.0.0.0", "InstallLocation": ""}
]"""

SAMPLE_PROVISIONED_JSON = """[
    {"DisplayName": "Clipchamp.Clipchamp", "PackageName": "Clipchamp.Clipchamp_2.0.0.0_neutral"},
    {"DisplayName": "Microsoft.Copilot", "PackageName": "Microsoft.Copilot_1.0.0.0_neutral"}
]"""


class TestBloatwareList:
    def test_bloatware_list_has_known_packages(self):
        assert "Microsoft.BingWeather" in BLOATWARE_LIST
        assert "Microsoft.SkypeApp" in BLOATWARE_LIST
        assert "Clipchamp.Clipchamp" in BLOATWARE_LIST
        assert "Microsoft.Copilot" in BLOATWARE_LIST

    def test_no_duplicates(self):
        assert len(BLOATWARE_LIST) == len(set(BLOATWARE_LIST))


class TestListInstalledBloatware:
    @patch("app.utils.bloatware.run")
    def test_finds_matching_packages(self, mock_run):
        mock1 = MagicMock()
        mock1.stdout = SAMPLE_PACKAGES_JSON
        mock1.returncode = 0
        mock2 = MagicMock()
        mock2.stdout = SAMPLE_PROVISIONED_JSON
        mock2.returncode = 0
        mock_run.side_effect = [mock1, mock2]

        result = list_installed_bloatware()
        names = [p["Name"] for p in result]
        assert "Microsoft.BingWeather" in names
        assert "Microsoft.SkypeApp" in names
        assert "Clipchamp.Clipchamp" in names
        assert "Microsoft.Copilot" in names
        assert "SomeOtherApp" not in names

    @patch("app.utils.bloatware.run", return_value=None)
    def test_handles_none_result(self, mock_run):
        result = list_installed_bloatware()
        assert result == []

    @patch("app.utils.bloatware.run")
    def test_deduplicates(self, mock_run):
        mock1 = MagicMock()
        mock1.stdout = SAMPLE_PACKAGES_JSON
        mock1.returncode = 0
        mock2 = MagicMock()
        mock2.stdout = """[{"DisplayName": "Microsoft.BingWeather", "PackageName": "Microsoft.BingWeather_8wekyb3d8bbwe"}]"""
        mock2.returncode = 0
        mock_run.side_effect = [mock1, mock2]

        result = list_installed_bloatware()
        bing = [p for p in result if p["Name"] == "Microsoft.BingWeather"]
        assert len(bing) == 1

    @patch("app.utils.bloatware.run", return_value=MagicMock(stdout="", returncode=0))
    def test_handles_empty_stdout(self, mock_run):
        result = list_installed_bloatware()
        assert result == []


class TestUninstallPackage:
    @patch("app.utils.bloatware.run_admin")
    def test_uninstall_success(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0, stdout="")
        assert uninstall_package("pkg_full_name") is True

    @patch("app.utils.bloatware.run_admin", return_value=None)
    def test_uninstall_none(self, mock_run_admin):
        assert uninstall_package("pkg_full_name") is False

    @patch("app.utils.bloatware.run_admin")
    def test_uninstall_provisioned(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0, stdout="")
        assert uninstall_package("pkg_full_name", provisioned=True) is True
        call_cmd = mock_run_admin.call_args[0][0]
        assert "Remove-AppxProvisionedPackage" in call_cmd

    @patch("app.utils.bloatware.run_admin")
    def test_uninstall_non_provisioned(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0, stdout="")
        assert uninstall_package("pkg_full_name", provisioned=False) is True
        call_cmd = mock_run_admin.call_args[0][0]
        assert "Remove-AppxPackage" in call_cmd
