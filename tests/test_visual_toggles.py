from unittest.mock import patch, MagicMock
from app.utils.visual_toggles import get_visual_status, toggle_animations, toggle_startup_sound, toggle_transparency, toggle_performance_mode


class TestGetVisualStatus:
    @patch("app.utils.visual_toggles.run")
    @patch("app.utils.visual_toggles.run_admin")
    def test_returns_status(self, mock_run_admin, mock_run):
        mock_run.side_effect = [
            MagicMock(stdout="1\n", returncode=0),
            MagicMock(stdout="0\n", returncode=0),
        ]
        mock_run_admin.return_value = MagicMock(stdout="0\n", returncode=0)
        status = get_visual_status()
        assert status["animations"] is True
        assert status["startup_sound"] is True
        assert status["transparency"] is False

    @patch("app.utils.visual_toggles.run", side_effect=Exception("boom"))
    def test_handles_exceptions(self, mock_run):
        status = get_visual_status()
        assert status.get("animations") is None


class TestToggleAnimations:
    @patch("app.utils.visual_toggles.run")
    def test_enable(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        assert toggle_animations(True) is True

    @patch("app.utils.visual_toggles.run")
    def test_disable(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        assert toggle_animations(False) is True


class TestToggleStartupSound:
    @patch("app.utils.visual_toggles.run_admin")
    def test_enable(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert toggle_startup_sound(True) is True
        cmd = mock_run_admin.call_args[0][0]
        assert "Remove-ItemProperty" in cmd

    @patch("app.utils.visual_toggles.run_admin")
    def test_disable(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert toggle_startup_sound(False) is True
        cmd = mock_run_admin.call_args[0][0]
        assert "New-ItemProperty" in cmd

    @patch("app.utils.visual_toggles.run_admin", return_value=None)
    def test_failure(self, mock_run_admin):
        assert toggle_startup_sound(True) is False


class TestToggleTransparency:
    @patch("app.utils.visual_toggles.run")
    def test_enable(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        assert toggle_transparency(True) is True

    @patch("app.utils.visual_toggles.run")
    def test_disable(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        assert toggle_transparency(False) is True


class TestTogglePerformanceMode:
    @patch("app.utils.visual_toggles.run")
    def test_enable(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        assert toggle_performance_mode(True) is True

    @patch("app.utils.visual_toggles.run")
    def test_disable(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        assert toggle_performance_mode(False) is True
