import re
from pathlib import Path

from backend.logger import log
from config.defaults import DEFAULT_SETTINGS, GAMES, TOOLS


class GamesManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):

        self.game_name = DEFAULT_SETTINGS["game"]
        self.game_meta = GAMES[self.game_name]
        self.game_display_name = self.game_meta["display_name"]

        self.game_installation, self.game_path = self.detect_game_installation()

        # self.game_installation = "steam" # !delme
        # self.game_path = Path("C:/test") # !delme
        if self.game_installation:

            self.shipping_exe = (
                Path(self.game_path)
                / self.game_meta[self.game_installation]["shipping_exe_suffix"]
            )

            self.vanilla_files = [
                {
                    "archive": Path(self.game_path) / suffix,
                    "unpacked": Path.cwd()
                    / TOOLS["tools_base"]
                    / "vanilla_unpacked"
                    / Path(suffix).stem,
                }
                for suffix in self.game_meta[self.game_installation][
                    "vanilla_archives_suffixes"
                ]
            ]
            self.mods_path = (
                Path(self.game_path)
                / self.game_meta[self.game_installation]["mods_path_suffix"]
            )
            # print(self.vanilla_files) # !delme

    def detect_game_installation(self):
        if steam_path := self.find_steam_game_path(self.game_meta["steam"]["steam_id"]):
            steam_path = str(Path(steam_path))
            log.debug(f"Steam installation found: {steam_path}")
            return "steam", steam_path

        if game_pass_path := self.find_game_pass_game_path(
            self.game_meta["game_pass"]["game_pass_id"]
        ):
            game_pass_path = str(Path(game_pass_path))
            log.debug(f"Game Pass installation found: {game_pass_path}")
            return "game_pass", game_pass_path

        fallback_path = str(Path(self.game_meta["fallback_path"]))
        log.debug(f"No installation found, using fallback path: {fallback_path}")
        return None, fallback_path

    def find_steam_game_path(self, game_id):
        try:
            import winreg

            key_path = r"SOFTWARE\WOW6432Node\Valve\Steam"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                steam_path = Path(winreg.QueryValueEx(key, "InstallPath")[0])

            steamapps_path = steam_path / "steamapps"
            library_folders_file = steamapps_path / "libraryfolders.vdf"
            if not library_folders_file.exists():
                return None

            library_paths = [steamapps_path]
            with library_folders_file.open("r") as file:
                content = file.read()
                matches = re.findall(r'"path"\s+"([^"]+)"', content)
                library_paths.extend(Path(match) / "steamapps" for match in matches)

            for library_path in library_paths:
                appmanifest_path = library_path / f"appmanifest_{game_id}.acf"
                if appmanifest_path.exists():
                    with appmanifest_path.open("r") as manifest_file:
                        content = manifest_file.read()
                        install_dir_match = re.search(
                            r'"installdir"\s+"([^"]+)"', content
                        )
                        if install_dir_match:
                            install_dir = install_dir_match.group(1)
                            game_path = library_path / "common" / install_dir
                            if game_path.exists():
                                return str(game_path)
            return None
        except Exception:
            return None

    def find_game_pass_game_path(self, game_id):
        log.debug("Game Pass installation detection isn't implemented.")
        return None
