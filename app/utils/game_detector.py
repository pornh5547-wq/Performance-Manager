import os
import glob
import subprocess
import json
import re
from app.utils._pwsh import run
from app.config import log

NO_WINDOW = subprocess.CREATE_NO_WINDOW
SI = subprocess.STARTUPINFO()
SI.dwFlags |= subprocess.STARTF_USESHOWWINDOW
SI.wShowWindow = subprocess.SW_HIDE

class GameDetector:
    def __init__(self):
        self.games = []
        self.platforms = {
            "Steam": "detect_steam_games",
            "Xbox App": "detect_xbox_games",
            "Battle.net": "detect_battlenet_games",
            "Epic Games": "detect_epic_games",
        }

    def detect_all(self):
        self.games = []
        for platform, method_name in self.platforms.items():
            try:
                games = getattr(self, method_name)()
                for game in games:
                    game["platform"] = platform
                self.games.extend(games)
            except Exception as e:
                log(f"Game detection error ({platform}): {str(e)}")
        self.games.sort(key=lambda g: g.get("name", "").lower())
        return self.games

    def detect_steam_games(self):
        games = []
        steam_paths = [
            "C:\\Program Files (x86)\\Steam",
            "C:\\Program Files\\Steam",
            os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'Steam'),
        ]
        steam_path = None
        for p in steam_paths:
            if os.path.exists(p):
                steam_path = p
                break
        if not steam_path:
            try:
                result = subprocess.run(
                    ['powershell', '-NoProfile', '-Command', '(Get-ItemProperty -Path "HKLM:\\SOFTWARE\\WOW6432Node\\Valve\\Steam" -Name InstallPath).InstallPath'],
                    capture_output=True, text=True, startupinfo=SI, creationflags=NO_WINDOW
                )
                if result.stdout.strip():
                    steam_path = result.stdout.strip()
            except:
                pass
        if steam_path:
            library_paths = [os.path.join(steam_path, 'steamapps')]
            library_file = os.path.join(steam_path, 'steamapps', 'libraryfolders.vdf')
            if os.path.exists(library_file):
                try:
                    with open(library_file, 'r') as f:
                        content = f.read()
                    for match in re.finditer(r'"path"\s+"([^"]+)"', content):
                        path = match.group(1)
                        apps_path = os.path.join(path, 'steamapps')
                        if os.path.exists(apps_path):
                            library_paths.append(apps_path)
                except:
                    pass
            for lib_path in library_paths:
                if os.path.exists(lib_path):
                    for acf in glob.glob(os.path.join(lib_path, 'appmanifest_*.acf')):
                        try:
                            with open(acf, 'r', errors='ignore') as f:
                                acf_content = f.read()
                            name_match = re.search(r'"name"\s+"([^"]+)"', acf_content)
                            appid_match = re.search(r'"appid"\s+"(\d+)"', acf_content)
                            installdir_match = re.search(r'"installdir"\s+"([^"]+)"', acf_content)
                            if name_match:
                                appid = appid_match.group(1) if appid_match else ""
                                installdir = installdir_match.group(1) if installdir_match else ""
                                install_path = os.path.join(lib_path, 'common', installdir) if installdir else lib_path
                                games.append({
                                    "name": name_match.group(1),
                                    "appid": appid,
                                    "install_path": install_path,
                                })
                        except:
                            pass
        return games

    def detect_xbox_games(self):
        games = []
        xbox_paths = [
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WindowsApps'),
            "C:\\XboxGames",
            os.path.join(os.environ.get('ProgramFiles', ''), 'WindowsApps'),
        ]
        seen = set()
        for base_path in xbox_paths:
            if os.path.exists(base_path):
                try:
                    for item in os.listdir(base_path):
                        item_path = os.path.join(base_path, item)
                        if os.path.isdir(item_path):
                            for root, dirs, files in os.walk(item_path):
                                for f in files:
                                    if f.endswith('.exe') and not f.lower().startswith('xbox'):
                                        name = os.path.splitext(f)[0]
                                        if name not in seen:
                                            seen.add(name)
                                            games.append({
                                                "name": name,
                                                "appid": "",
                                                "install_path": root,
                                                "executable": os.path.join(root, f),
                                            })
                                            break
                except:
                    pass
        result = run('Get-ChildItem -Path "$env:LOCALAPPDATA\\Microsoft\\WindowsApps" -Filter *.exe -Recurse -ErrorAction SilentlyContinue | Select-Object Name, FullName | ConvertTo-Json')
        if result and result.stdout.strip():
            try:
                items = json.loads(result.stdout)
                if not isinstance(items, list):
                    items = [items]
                for item in items:
                    name = item.get('Name', '').replace('.exe', '')
                    if name not in seen and name:
                        seen.add(name)
                        games.append({
                            "name": name,
                            "appid": "",
                            "install_path": os.path.dirname(item.get('FullName', '')),
                            "executable": item.get('FullName', ''),
                        })
            except:
                pass
        return games

    def detect_battlenet_games(self):
        games = []
        battlenet_paths = [
            "C:\\Program Files (x86)\\Battle.net",
            os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'Battle.net'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Battle.net'),
        ]
        for base in battlenet_paths:
            if os.path.exists(base):
                for root, dirs, files in os.walk(base):
                    if 'Battle.net.exe' in files or 'Blizzard.exe' in files:
                        continue
                    for f in files:
                        if f.endswith('.exe') and f.lower() not in ['battle.net.exe', 'blizzard.exe', 'agent.exe', 'updater.exe']:
                            name = os.path.splitext(f)[0]
                            games.append({
                                "name": name,
                                "appid": "",
                                "install_path": root,
                                "executable": os.path.join(root, f),
                            })
                            break
        result = run('Get-ItemProperty -Path "HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*", "HKLM:\\SOFTWARE\\WOW6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*" | Where-Object {$_.Publisher -like "*Blizzard*" -or $_.Publisher -like "*Activision*"} | Select-Object DisplayName, InstallLocation | ConvertTo-Json')
        if result and result.stdout.strip():
            try:
                items = json.loads(result.stdout)
                if not isinstance(items, list):
                    items = [items]
                for item in items:
                    name = item.get('DisplayName', '')
                    loc = item.get('InstallLocation', '')
                    if name and name not in [g['name'] for g in games]:
                        games.append({
                            "name": name,
                            "appid": "",
                            "install_path": loc,
                        })
            except:
                pass
        return games

    def detect_epic_games(self):
        games = []
        manifest_paths = [
            os.path.join(os.environ.get('PROGRAMDATA', 'C:\\ProgramData'), 'Epic', 'EpicGamesLauncher', 'Data', 'Manifests'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'EpicGamesLauncher', 'Saved', 'Config', 'Windows'),
        ]
        for manifest_dir in manifest_paths:
            if os.path.exists(manifest_dir):
                for item in os.listdir(manifest_dir):
                    if item.endswith('.item'):
                        try:
                            with open(os.path.join(manifest_dir, item), 'r', errors='ignore') as f:
                                content = f.read()
                            name_match = re.search(r'"DisplayName"\s*:\s*"([^"]+)"', content)
                            loc_match = re.search(r'"InstallLocation"\s*:\s*"([^"]+)"', content)
                            if name_match:
                                games.append({
                                    "name": name_match.group(1),
                                    "appid": "",
                                    "install_path": loc_match.group(1) if loc_match else "",
                                })
                        except:
                            pass
        return games

    def get_game_count(self):
        return len(self.games)

    def launch_game(self, game):
        if game.get("platform") == "Steam" and game.get("appid"):
            steam_path = "C:\\Program Files (x86)\\Steam\\steam.exe"
            alt_steam = os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'Steam', 'steam.exe')
            for sp in [steam_path, alt_steam]:
                if os.path.exists(sp):
                    subprocess.Popen([sp, f'steam://rungameid/{game["appid"]}'],
                                     startupinfo=SI, creationflags=NO_WINDOW)
                    log(f"Launched Steam game: {game['name']}")
                    return True
        exe = game.get("executable", "")
        install_path = game.get("install_path", "")
        if exe and os.path.exists(exe):
            subprocess.Popen([exe], cwd=os.path.dirname(exe), startupinfo=SI, creationflags=NO_WINDOW)
            log(f"Launched game: {game['name']}")
            return True
        if install_path and os.path.exists(install_path):
            for root, dirs, files in os.walk(install_path):
                for f in files:
                    if f.endswith('.exe') and 'uninstall' not in f.lower() and 'setup' not in f.lower():
                        subprocess.Popen([os.path.join(root, f)], cwd=root, startupinfo=SI, creationflags=NO_WINDOW)
                        log(f"Launched game: {game['name']} via {f}")
                        return True
        log(f"Could not launch game: {game['name']}")
        return False
