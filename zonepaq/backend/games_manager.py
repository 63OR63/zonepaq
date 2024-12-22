import re
from pathlib import Path

from config.defaults import DEFAULT_SETTINGS, GAMES


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

        if self.game_installation:

            self.shipping_exe = (
                Path(self.game_path)
                / self.game_meta[self.game_installation]["shipping_exe_suffix"]
            )
            self.vanilla_archives = [
                Path(self.game_path)
                / self.game_meta[self.game_installation]["vanilla_archives_suffix"]
                for suffix in self.game_meta[self.game_installation][
                    "vanilla_archives_suffix"
                ]
            ]
            self.mods_path = (
                Path(self.game_path)
                / self.game_meta[self.game_installation]["mods_path_suffix"]
            )

    def detect_game_installation(self):

        if steam_path := self.find_steam_game_path(self.game_meta["steam"]["steam_id"]):
            return "steam", str(Path(steam_path))
        # if game_pass_path := self.find_game_pass_game_path(
        #     self.game_meta["game_pass"]["game_pass_id"]
        # ):
        #     return "game_pass", str(Path(game_pass_path))

        return None, str(Path(self.game_meta["fallback_path"]))

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
