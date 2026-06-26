from unittest.mock import patch, MagicMock
from app.utils.large_files import scan_directory, format_size


class TestScanDirectory:
    @patch("os.walk")
    @patch("os.path.getsize")
    def test_finds_large_files(self, mock_gs, mock_walk):
        mock_walk.return_value = [("/test", [], ["small.txt", "large.bin"])]
        mock_gs.side_effect = [50 * 1024, 200 * 1024 * 1024]
        results = scan_directory("/test", min_size_mb=100)
        assert len(results) == 1
        assert results[0]["name"] == "large.bin"
        assert results[0]["size"] == 200 * 1024 * 1024
        assert results[0]["dir"] == "/test"

    @patch("os.walk", side_effect=PermissionError)
    def test_handles_permission_error(self, mock_walk):
        results = scan_directory("C:\\Windows", min_size_mb=100)
        assert results == []

    @patch("os.walk")
    @patch("os.path.getsize", side_effect=OSError)
    def test_skips_inaccessible_files(self, mock_gs, mock_walk):
        mock_walk.return_value = [("/test", [], ["locked.bin"])]
        results = scan_directory("/test", min_size_mb=100)
        assert results == []

    @patch("os.walk")
    @patch("os.path.getsize", return_value=500 * 1024 * 1024)
    def test_callback_invoked(self, mock_gs, mock_walk):
        mock_walk.return_value = [("/test", [], [f"f{i}.bin" for i in range(100)])]
        callback = MagicMock()
        results = scan_directory("/test", min_size_mb=100, callback=callback)
        assert len(results) == 100
        assert callback.called


class TestFormatSize:
    def test_bytes(self):
        assert format_size(500) == "500.0 B"

    def test_kb(self):
        assert format_size(2048) == "2.0 KB"

    def test_mb(self):
        assert format_size(10 * 1024 * 1024) == "10.0 MB"

    def test_gb(self):
        assert format_size(2 * 1024**3) == "2.0 GB"
