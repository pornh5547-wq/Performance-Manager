import signal
from unittest.mock import patch, MagicMock
from app.utils import speed_test


class TestTestLatency:
    @patch("subprocess.run")
    def test_returns_latency_results(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)
        results = speed_test.test_latency()
        assert len(results) == 3
        hosts = [r["host"] for r in results]
        assert "8.8.8.8" in hosts
        assert "1.1.1.1" in hosts
        assert "google.com" in hosts
        for r in results:
            assert r["latency_ms"] is not None

    @patch("subprocess.run", side_effect=Exception("timeout"))
    def test_handles_timeout(self, mock_run):
        results = speed_test.test_latency()
        for r in results:
            assert r["latency_ms"] is None


class TestDownloadSpeed:
    def _call_with_timeout(self, func, timeout=5):
        import threading
        result = [None]
        exc = [None]
        def runner():
            try:
                result[0] = func()
            except Exception as e:
                exc[0] = e
        t = threading.Thread(target=runner, daemon=True)
        t.start()
        t.join(timeout)
        if t.is_alive():
            raise TimeoutError("test timed out")
        if exc[0]:
            raise exc[0]
        return result[0]

    def test_returns_download_speed(self):
        mock_response = MagicMock()
        chunk_data = b"x" * 8192
        mock_response.read.side_effect = [chunk_data, chunk_data, b""]
        with patch("urllib.request.urlopen", return_value=mock_response):
            with patch("time.time", side_effect=[100.0, 102.0]):
                result = self._call_with_timeout(lambda: speed_test.test_download_speed())
                assert "download_mbps" in result
                assert result["total_bytes"] == 16384
                assert "elapsed_sec" in result

    def test_handles_error(self):
        with patch("urllib.request.urlopen", side_effect=Exception("connection failed")):
            result = self._call_with_timeout(lambda: speed_test.test_download_speed())
            assert "error" in result
