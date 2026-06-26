from unittest.mock import patch, mock_open
from app.utils.hosts_editor import read_hosts, add_entry, remove_entry, toggle_entry, restore_defaults


SAMPLE_HOSTS = """# Copyright (c) 1993-2009 Microsoft Corp.
#
127.0.0.1       localhost
::1             localhost
# 0.0.0.0   example.com
192.168.1.1     router.local
"""


class TestReadHosts:
    @patch("builtins.open", new_callable=mock_open, read_data=SAMPLE_HOSTS)
    @patch("os.path.exists", return_value=True)
    def test_reads_all_entries(self, mock_exists, mock_file):
        entries = read_hosts()
        assert len(entries) == 6
        active = [e for e in entries if not e.get("comment")]
        assert len(active) == 3
        assert active[0]["ip"] == "127.0.0.1"
        assert active[0]["domain"] == "localhost"
        assert active[0]["redirected"] is True

    @patch("os.path.exists", return_value=False)
    def test_no_hosts_file(self, mock_exists):
        entries = read_hosts()
        assert entries == []

    @patch("builtins.open", side_effect=PermissionError)
    @patch("os.path.exists", return_value=True)
    def test_permission_error(self, mock_exists, mock_open_file):
        entries = read_hosts()
        assert entries == []


class TestToggleEntry:
    def test_toggle_comment_uncomments(self):
        entry = {"line": 4, "raw": "# 0.0.0.0   example.com", "comment": False, "ip": "0.0.0.0", "domain": "example.com"}
        with patch("builtins.open", new_callable=mock_open, read_data=SAMPLE_HOSTS):
            with patch("os.path.exists", return_value=True):
                ok = toggle_entry(entry)
                assert ok is True

    def test_toggle_comment_returns_false(self):
        entry = {"comment": True}
        assert toggle_entry(entry) is False


class TestAddEntry:
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    def test_adds_entry(self, mock_exists, mock_file):
        ok = add_entry("127.0.0.1", "test.local")
        assert ok is True
        mock_file().write.assert_called()


class TestRemoveEntry:
    @patch("builtins.open", new_callable=mock_open, read_data=SAMPLE_HOSTS)
    @patch("os.path.exists", return_value=True)
    def test_removes_entry(self, mock_exists, mock_file):
        ok = remove_entry("example.com")
        assert ok is True

    @patch("builtins.open", side_effect=PermissionError)
    @patch("os.path.exists", return_value=True)
    def test_permission_error(self, mock_exists, mock_file):
        ok = remove_entry("test.local")
        assert ok is False


class TestRestoreDefaults:
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.path.exists", return_value=True)
    def test_restores_defaults(self, mock_exists, mock_file):
        ok = restore_defaults()
        assert ok is True
