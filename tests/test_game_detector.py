import os
import subprocess
from unittest.mock import patch, MagicMock, mock_open
from app.utils.game_detector import GameDetector, SI

SAMPLE_ACF = '''
"AppState"
{
    "appid" "123456"
    "name" "Test Game"
    "installdir" "TestGame"
    "StateFlags" "4"
}
'''

SAMPLE_LIBRARY_VDF = '''
"libraryfolders"
{
    "1"
    {
        "path" "D:\\\\SteamLibrary"
    }
}
'''


class TestGameDetector:
    def setup_method(self):
        self.detector = GameDetector()

    @patch("os.path.exists", return_value=True)
    @patch("glob.glob", return_value=["appmanifest_123456.acf"])
    @patch("builtins.open", new_callable=mock_open, read_data=SAMPLE_ACF)
    def test_detect_steam_games_extracts_installdir(self, mock_file, mock_glob, mock_exists):
        games = self.detector.detect_steam_games()
        assert len(games) >= 1
        found = [g for g in games if g["name"] == "Test Game"]
        assert len(found) == 1
        assert found[0]["appid"] == "123456"
        assert found[0]["install_path"].endswith("common\\TestGame")

    @patch("os.path.exists", return_value=False)
    def test_detect_steam_games_no_steam(self, mock_exists):
        games = self.detector.detect_steam_games()
        assert games == []

    @patch("os.path.exists", return_value=True)
    @patch("glob.glob", return_value=[])
    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_detect_steam_no_acf_files(self, mock_file, mock_glob, mock_exists):
        games = self.detector.detect_steam_games()
        assert games == []

    @patch.object(GameDetector, "detect_steam_games", return_value=[{"name": "G1"}, {"name": "G2"}])
    @patch.object(GameDetector, "detect_xbox_games", return_value=[{"name": "X1"}])
    @patch.object(GameDetector, "detect_battlenet_games", return_value=[])
    @patch.object(GameDetector, "detect_epic_games", return_value=[])
    def test_detect_all(self, e, b, x, s):
        games = self.detector.detect_all()
        names = [g["name"] for g in games]
        assert "G1" in names
        assert "G2" in names
        assert "X1" in names
        for g in games:
            assert "platform" in g

    def test_get_game_count(self):
        self.detector.games = [{"name": "A"}, {"name": "B"}]
        assert self.detector.get_game_count() == 2

    def test_get_game_count_empty(self):
        self.detector.games = []
        assert self.detector.get_game_count() == 0


class TestLaunchGame:
    def setup_method(self):
        self.detector = GameDetector()

    @patch("subprocess.Popen")
    @patch("os.path.exists", return_value=True)
    def test_launch_steam_game(self, mock_exists, mock_popen):
        game = {"name": "Test", "appid": "123", "platform": "Steam"}
        assert self.detector.launch_game(game) is True
        mock_popen.assert_called_once()
        args = mock_popen.call_args[0][0]
        assert "steam.exe" in args[0]
        assert "steam://rungameid/123" in args[1]

    @patch("subprocess.Popen")
    @patch("os.path.exists", return_value=True)
    def test_launch_with_exe(self, mock_exists, mock_popen):
        game = {"name": "Test", "executable": "C:\\game\\game.exe", "install_path": "C:\\game"}
        assert self.detector.launch_game(game) is True
        mock_popen.assert_called_once_with(["C:\\game\\game.exe"], cwd="C:\\game", startupinfo=SI, creationflags=subprocess.CREATE_NO_WINDOW)

    @patch("subprocess.Popen")
    @patch("os.path.exists", side_effect=lambda p: True)
    @patch("os.walk", return_value=[("C:\\game", [], ["launcher.exe", "uninstall.exe"])])
    def test_launch_with_os_walk(self, mock_walk, mock_exists, mock_popen):
        game = {"name": "Test", "install_path": "C:\\game"}
        assert self.detector.launch_game(game) is True
        args = mock_popen.call_args[0][0]
        assert "launcher.exe" in args[0]

    @patch("os.path.exists", return_value=False)
    def test_launch_failure(self, mock_exists):
        game = {"name": "Test"}
        assert self.detector.launch_game(game) is False
