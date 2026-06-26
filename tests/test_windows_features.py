from unittest.mock import patch, MagicMock
from app.utils.windows_features import list_features, enable_feature, disable_feature, COMMON_FEATURES


SAMPLE_FEATURES_JSON = """[
    {"FeatureName": "Microsoft-Hyper-V", "DisplayName": "Hyper-V", "State": "Enabled", "Description": "Virtualization"},
    {"FeatureName": "VirtualMachinePlatform", "DisplayName": "Virtual Machine Platform", "State": "Disabled", "Description": ""},
    {"FeatureName": "TelnetClient", "DisplayName": "Telnet Client", "State": "Disabled", "Description": ""}
]"""


class TestListFeatures:
    @patch("app.utils.windows_features.run")
    def test_returns_features_list(self, mock_run):
        mock_run.return_value = MagicMock(stdout=SAMPLE_FEATURES_JSON, returncode=0)
        features = list_features()
        assert len(features) == 3
        names = [f["FeatureName"] for f in features]
        assert "Microsoft-Hyper-V" in names
        assert "VirtualMachinePlatform" in names
        assert "TelnetClient" in names

    @patch("app.utils.windows_features.run", return_value=None)
    def test_returns_empty_on_none(self, mock_run):
        assert list_features() == []

    @patch("app.utils.windows_features.run")
    def test_handles_single_item(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout='{"FeatureName": "TestFeature", "DisplayName": "Test", "State": "Enabled"}',
            returncode=0
        )
        features = list_features()
        assert len(features) == 1

    @patch("app.utils.windows_features.run", return_value=MagicMock(stdout="bad json", returncode=0))
    def test_invalid_json(self, mock_run):
        assert list_features() == []


class TestCommonFeatures:
    def test_has_known_features(self):
        names = dict(COMMON_FEATURES)
        assert "Microsoft-Hyper-V" in names
        assert "VirtualMachinePlatform" in names
        assert "NetFx3" in names
        assert len(COMMON_FEATURES) >= 10


class TestFeatureActions:
    @patch("app.utils.windows_features.run_admin")
    def test_enable_feature(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert enable_feature("Microsoft-Hyper-V") is True
        cmd = mock_run_admin.call_args[0][0]
        assert "Enable-WindowsOptionalFeature" in cmd
        assert "Microsoft-Hyper-V" in cmd

    @patch("app.utils.windows_features.run_admin")
    def test_disable_feature(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert disable_feature("Microsoft-Hyper-V") is True
        cmd = mock_run_admin.call_args[0][0]
        assert "Disable-WindowsOptionalFeature" in cmd
        assert "Microsoft-Hyper-V" in cmd

    @patch("app.utils.windows_features.run_admin", return_value=None)
    def test_returns_false_on_none(self, mock_run_admin):
        assert enable_feature("Any") is False
        assert disable_feature("Any") is False
