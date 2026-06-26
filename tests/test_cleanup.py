from unittest.mock import patch, MagicMock, mock_open
from app.utils.cleanup import (
    get_size, format_size, clean_temp_files, clean_shader_cache,
    clean_prefetch, clean_browser_cache, get_total_cleanable_size, run_full_cleanup
)


class TestFormatSize:
    def test_bytes(self):
        assert format_size(500) == "500.0 B"

    def test_kb(self):
        assert format_size(2048) == "2.0 KB"

    def test_mb(self):
        assert format_size(5 * 1024 * 1024) == "5.0 MB"

    def test_gb(self):
        assert format_size(3 * 1024**3) == "3.0 GB"

    def test_tb(self):
        assert format_size(2 * 1024**4) == "2.0 TB"


class TestGetSize:
    def test_file_size(self):
        with patch("os.path.isfile", return_value=True):
            with patch("os.path.getsize", return_value=1234):
                assert get_size("/some/file") == 1234

    def test_directory_size(self):
        with patch("os.path.isfile", return_value=False):
            with patch("os.path.isdir", return_value=True):
                with patch("os.walk", return_value=[("/d", [], ["a.txt", "b.bin"])]):
                    with patch("os.path.getsize", side_effect=[100, 200]):
                        with patch("os.path.exists", return_value=True):
                            assert get_size("/d") == 300

    def test_nonexistent(self):
        with patch("os.path.isfile", return_value=False):
            with patch("os.path.isdir", return_value=False):
                assert get_size("/void") == 0


class TestCleanTempFiles:
    @patch("os.listdir")
    @patch("os.path.exists")
    @patch("os.path.isfile")
    @patch("os.path.islink")
    @patch("os.path.isdir")
    @patch("os.unlink")
    @patch("shutil.rmtree")
    @patch("os.path.getsize")
    def test_cleans_temp(self, gs, rmtree, unlink, isdir, islink, isfile, exists, listdir):
        exists.return_value = True
        isfile.side_effect = lambda p: "file" in p
        islink.return_value = False
        isdir.side_effect = lambda p: "dir" in p
        gs.return_value = 1024
        listdir.return_value = ["file1.tmp", "dir1"]
        result = clean_temp_files()
        assert result["cleaned"] >= 1
        assert result["freed_bytes"] >= 0

    @patch("os.listdir", side_effect=PermissionError)
    @patch("os.path.exists", return_value=True)
    def test_handles_permission_error(self, exists, listdir):
        result = clean_temp_files()
        assert "errors" in result


class TestCleanShaderCache:
    @patch("os.path.exists", return_value=True)
    @patch("shutil.rmtree")
    @patch("app.utils.cleanup.get_size", return_value=1048576)
    def test_cleans_shader_cache(self, gs, rmtree, exists):
        result = clean_shader_cache()
        assert result["cleaned"] >= 1
        assert result["freed_bytes"] == 4 * 1048576


class TestCleanPrefetch:
    @patch("os.path.exists", return_value=True)
    @patch("glob.glob", return_value=["a.pf", "b.pf"])
    @patch("os.path.getsize", side_effect=[512, 1024])
    @patch("os.remove")
    def test_cleans_prefetch(self, remove, gs, glob, exists):
        result = clean_prefetch()
        assert result["cleaned"] == 2
        assert result["freed_bytes"] == 1536


class TestCleanBrowserCache:
    @patch("os.path.exists", return_value=True)
    @patch("shutil.rmtree")
    @patch("app.utils.cleanup.get_size", return_value=2097152)
    def test_cleans_browser_cache(self, gs, rmtree, exists):
        result = clean_browser_cache()
        assert result["cleaned"] >= 1
        assert result["freed_bytes"] >= 2097152


class TestGetTotalCleanableSize:
    @patch("os.path.exists", return_value=True)
    @patch("app.utils.cleanup.get_size", return_value=1000)
    def test_sums_sizes(self, gs, exists):
        total = get_total_cleanable_size()
        assert total > 0


class TestRunFullCleanup:
    @patch("app.utils.cleanup.clean_temp_files", return_value={"freed_bytes": 1000})
    @patch("app.utils.cleanup.clean_shader_cache", return_value={"freed_bytes": 2000})
    @patch("app.utils.cleanup.clean_browser_cache", return_value={"freed_bytes": 3000})
    @patch("app.utils.cleanup.clean_prefetch", return_value={"freed_bytes": 500})
    def test_full_cleanup_returns_results(self, cp, cb, cs, ct):
        results, total = run_full_cleanup()
        assert total == 6500
        assert results["temp"]["freed_bytes"] == 1000
        assert results["shader"]["freed_bytes"] == 2000
        assert results["browser"]["freed_bytes"] == 3000
        assert results["prefetch"]["freed_bytes"] == 500
