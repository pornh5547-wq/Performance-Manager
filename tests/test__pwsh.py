import subprocess
from unittest.mock import patch, MagicMock
from app.utils._pwsh import run, run_admin


class TestRun:
    def test_run_returns_result_on_success(self):
        mock = MagicMock()
        mock.stdout = "hello"
        mock.returncode = 0
        with patch("subprocess.run", return_value=mock):
            r = run("Get-Date")
            assert r.stdout == "hello"
            assert r.returncode == 0

    def test_run_returns_none_on_exception(self):
        with patch("subprocess.run", side_effect=Exception("boom")):
            r = run("bad cmd")
            assert r is None

    def test_run_shell_mode(self):
        mock = MagicMock()
        mock.stdout = "shell-out"
        with patch("subprocess.run", return_value=mock) as mocked:
            r = run("echo hi", shell=True)
            assert r.stdout == "shell-out"
            assert mocked.call_args[0][0] == "echo hi"
            assert mocked.call_args[1]["shell"] is True


class TestRunAdmin:
    def test_run_admin_constructs_command(self):
        mock = MagicMock()
        mock.stdout = ""
        mock.returncode = 0
        with patch("subprocess.run", return_value=mock) as mocked:
            r = run_admin("do-something")
            assert r is not None
            args = mocked.call_args[0]
            assert len(args) == 1
            cmd_list = args[0]
            assert cmd_list[0] == "powershell"
            assert "-NoProfile" in cmd_list
            cmd_str = cmd_list[-1]
            assert "Start-Process" in cmd_str
            assert "PowerShell" in cmd_str
            assert "-Verb RunAs" in cmd_str
            assert "-PassThru" in cmd_str
            assert "-Wait" in cmd_str
            assert "do-something" in cmd_str

    def test_run_admin_returns_none_on_exception(self):
        with patch("subprocess.run", side_effect=Exception("boom")):
            r = run_admin("anything")
            assert r is None

    def test_run_admin_timeout(self):
        with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="test", timeout=10)):
            r = run_admin("slow")
            assert r is None
