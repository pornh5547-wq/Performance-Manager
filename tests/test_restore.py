from unittest.mock import patch, MagicMock
from app.utils.restore import create_restore_point, list_restore_points, restore_system, enable_system_restore


class TestCreateRestorePoint:
    @patch("app.utils.restore.run_admin")
    def test_success(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0, stdout="ok")
        result = create_restore_point("Test")
        assert result["success"] is True
        assert result["output"] == "ok"

    @patch("app.utils.restore.run_admin", return_value=None)
    def test_failure(self, mock_run_admin):
        result = create_restore_point("Test")
        assert result["success"] is False
        assert result["output"] == "Failed"

    @patch("app.utils.restore.run_admin", side_effect=Exception("error"))
    def test_exception(self, mock_run_admin):
        result = create_restore_point("Test")
        assert result["success"] is False


class TestListRestorePoints:
    @patch("app.utils.restore.run_admin")
    def test_returns_points(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(
            stdout='[{"SequenceNumber": 1, "Description": "Test"}]\n', returncode=0
        )
        points = list_restore_points()
        assert len(points) == 1
        assert points[0]["SequenceNumber"] == 1

    @patch("app.utils.restore.run_admin")
    def test_handles_single_dict(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(
            stdout='{"SequenceNumber": 1, "Description": "Test"}\n', returncode=0
        )
        points = list_restore_points()
        assert len(points) == 1

    @patch("app.utils.restore.run_admin", return_value=None)
    def test_returns_empty_on_none(self, mock_run_admin):
        assert list_restore_points() == []

    @patch("app.utils.restore.run_admin")
    def test_returns_empty_on_invalid_json(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(stdout="not json", returncode=0)
        assert list_restore_points() == []


class TestRestoreSystem:
    @patch("app.utils.restore.run_admin")
    def test_success(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0, stdout="restored")
        result = restore_system(1)
        assert result["success"] is True
        assert result["output"] == "restored"

    @patch("app.utils.restore.run_admin", return_value=None)
    def test_failure(self, mock_run_admin):
        result = restore_system(1)
        assert result["success"] is False
        assert result["output"] == "Failed"


class TestEnableSystemRestore:
    @patch("app.utils.restore.run_admin")
    def test_success(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        result = enable_system_restore("D:")
        assert result["success"] is True
        assert "D:" in mock_run_admin.call_args[0][0]

    @patch("app.utils.restore.run_admin", return_value=None)
    def test_failure(self, mock_run_admin):
        result = enable_system_restore("C:")
        assert result["success"] is False
