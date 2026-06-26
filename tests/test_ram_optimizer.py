from unittest.mock import patch, MagicMock
from app.utils.ram_optimizer import get_memory_stats, get_top_memory_processes, empty_working_set, kill_process, clear_standby_list


class TestGetMemoryStats:
    @patch("psutil.virtual_memory")
    @patch("psutil.swap_memory")
    def test_returns_formatted_stats(self, mock_swap, mock_mem):
        mock_mem.return_value.total = 16 * 1024**3
        mock_mem.return_value.available = 8 * 1024**3
        mock_mem.return_value.used = 8 * 1024**3
        mock_mem.return_value.percent = 50.0
        mock_swap.return_value.total = 2 * 1024**3
        mock_swap.return_value.used = 0.5 * 1024**3
        mock_swap.return_value.percent = 25.0

        stats = get_memory_stats()
        assert stats["total_gb"] == 16.0
        assert stats["available_gb"] == 8.0
        assert stats["used_gb"] == 8.0
        assert stats["percent"] == 50.0
        assert stats["swap_total_gb"] == 2.0
        assert stats["swap_used_gb"] == 0.5
        assert stats["swap_percent"] == 25.0


class TestGetTopMemoryProcesses:
    @patch("psutil.process_iter")
    def test_returns_sorted_processes(self, mock_iter):
        mock_iter.return_value = [
            MagicMock(info={"pid": 1, "name": "chrome.exe", "memory_percent": 10.0, "memory_info": MagicMock(rss=500 * 1024 * 1024), "cpu_percent": 5.0, "status": "running"}),
            MagicMock(info={"pid": 2, "name": "python.exe", "memory_percent": 5.0, "memory_info": MagicMock(rss=200 * 1024 * 1024), "cpu_percent": 2.0, "status": "running"}),
        ]
        procs = get_top_memory_processes(5)
        assert len(procs) == 2
        assert procs[0]["name"] == "chrome.exe"
        assert "memory_mb" in procs[0]

    @patch("psutil.process_iter", side_effect=Exception("boom"))
    def test_handles_exception(self, mock_iter):
        assert get_top_memory_processes(5) == []


class TestEmptyWorkingSet:
    @patch("psutil.process_iter")
    @patch("ctypes.windll.kernel32.OpenProcess")
    @patch("ctypes.windll.kernel32.SetProcessWorkingSetSize")
    @patch("ctypes.windll.kernel32.CloseHandle")
    def test_empties_working_set(self, mock_close, mock_set, mock_open, mock_iter):
        mock_open.return_value = 123
        mock_iter.return_value = [
            MagicMock(info={"pid": 1, "name": "test.exe", "memory_info": MagicMock(rss=100 * 1024 * 1024)})
        ]
        result = empty_working_set()
        assert result["count"] >= 1
        assert result["freed_mb"] >= 100


class TestKillProcess:
    @patch("psutil.Process")
    def test_kill_success(self, mock_proc_cls):
        mock_proc = MagicMock()
        mock_proc_cls.return_value = mock_proc
        assert kill_process(1234) is True
        mock_proc.kill.assert_called_once()

    @patch("psutil.Process", side_effect=Exception("not found"))
    def test_kill_failure(self, mock_proc):
        assert kill_process(9999) is False


class TestClearStandbyList:
    @patch("app.utils.ram_optimizer.run_admin")
    def test_clear_standby_list_admin(self, mock_run_admin):
        mock_run_admin.return_value = MagicMock(returncode=0)
        assert clear_standby_list() is True

    @patch("app.utils.ram_optimizer.run_admin", return_value=None)
    def test_clear_standby_list_fallback(self, mock_run_admin):
        assert clear_standby_list() is True
