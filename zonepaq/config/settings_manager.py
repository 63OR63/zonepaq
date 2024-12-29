import re
import sys
import threading
from abc import ABC, abstractmethod
from pathlib import Path

from backend.logger import log
from backend.utilities import Files
from config.defaults import DEFAULT_SETTINGS, DEFAULT_TOOLS_PATHS, TOOLS


class ConfigSource(ABC):
    @abstractmethod
    def load(self) -> dict:
        pass

    @abstractmethod
    def save(self, config: dict) -> None:
        pass


class IniConfigSource(ConfigSource):
    def __init__(self, file_path):
        from configparser import ConfigParser

        self.file_path = Path(file_path)
        self.config = ConfigParser()

    def load(self) -> dict:
        if self.file_path.exists():
            self.config.read(self.file_path, encoding="utf-8")
        return {
            section: dict(self.config[section]) for section in self.config.sections()
        }

    def save(self, config: dict) -> None:
        for section, values in config.items():
            if section not in self.config:
                self.config.add_section(section)
            for key, value in values.items():
                self.config[section][key] = str(value)
        with self.file_path.open("w", encoding="utf-8") as file:
            self.config.write(file)


class ConfigurationLoader:
    def __init__(self, sources, defaults):
        self.sources = sources
        self.defaults = defaults

    def load(self) -> dict:
        merged_config = {
            section: values.copy() for section, values in self.defaults.items()
        }
        for source in self.sources:
            config = source.load()
            for section, values in config.items():
                if section not in merged_config:
                    merged_config[section] = {}
                merged_config[section].update(values)

        for source in self.sources:
            source.save(merged_config)

        return merged_config

    def save(self, config: dict) -> None:
        for source in self.sources:
            source.save(config)


class SettingsManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.initialize()
        return cls._instance

    def initialize(self):
        self.INI_SETTINGS_FILE = r"zonepaq\settings.ini"
        Files.create_dir(Path(self.INI_SETTINGS_FILE).parent)

        sources = [
            IniConfigSource(self.INI_SETTINGS_FILE),
        ]

        self.games_manager = GamesManager()

        defaults = {
            "SETTINGS": DEFAULT_SETTINGS,
            "TOOLS_PATHS": DEFAULT_TOOLS_PATHS,
            "GAME_PATHS": {
                self.games_manager.game_name: str(
                    Path(self.games_manager.get_game_path())
                )
            },
        }

        self.loader = ConfigurationLoader(sources, defaults)

        self.config = self.loader.load()

        self.load()

    def load(self):

        # shortcuts
        self.SETTINGS = self.get("SETTINGS")
        self.TOOLS_PATHS = self.get("TOOLS_PATHS")
        self.GAME_PATHS = self.get("GAME_PATHS")

        self.MERGING_ENGINE = self.get("SETTINGS", "merging_engine")
        self.LANG_NAME = self.get("SETTINGS", "lang_name")
        self.THEME_NAME = self.get("SETTINGS", "theme_name")
        self.SHOW_HINTS = self.get("SETTINGS", "show_hints")
        self.DARK_MODE = self.get("SETTINGS", "dark_mode")
        self.AES_KEY = self.get("SETTINGS", "aes_key")
        self.MERGED_PREFIX = self.get("SETTINGS", "merged_prefix")
        self.MERGED_STATIC_NAME = self.get("SETTINGS", "merged_static_name")

        # links
        self.TOOLS = TOOLS

        self.games_manager.update_paths(self.GAME_PATHS[self.games_manager.game_name])

    def update_config(self, section, key, value):
        self.config[section][key] = str(value)
        self.save()
        self.load()
        return self._instance

    def set(self, section, key, value):
        self.config[section][key] = str(value)
        self.load()
        return

    def get(self, section, key=None):
        if key is None:
            return self.config.get(section)
        return self.config.get(section).get(key)

    def save(self):
        self.loader.save(self.config)


GAMES = {
    "stalker_2": {
        "display_name": "S.T.A.L.K.E.R. 2",
        "installations": {
            "steam": {
                "display_name": "Steam",
                "steam_id": "1643320",
                "shipping_exe_suffix": "Stalker2/Binaries/Win64/Stalker2-Win64-Shipping.exe",
                "vanilla_archives_suffixes": [
                    "Stalker2/Content/Paks/pakchunk0-Windows.pak"
                ],
                "mods_path_suffix": "Stalker2/Content/Paks/~mods",
            },
            "game_pass": {
                "display_name": "Game Pass",
                "game_folder_name": "S.T.A.L.K.E.R. 2",
                "shipping_exe_suffix": "Content/Stalker2/Binaries/WinGDK/Stalker2-WinGDK-Shipping.exe",
                "vanilla_archives_suffixes": [
                    "Content/Stalker2/Content/Paks/pakchunk0-WinGDK.pak"
                ],
                "mods_path_suffix": "Stalker2/Content/Paks/~mods",
            },
        },
        "fallback_path": "Z:/Games/S.T.A.L.K.E.R. 2 Heart of Chornobyl",
    },
}


class GamesManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance.initialize()
        return cls._instance

    def initialize(self):

        self.game_name = DEFAULT_SETTINGS["game"]
        self.game_meta = GAMES[self.game_name]
        self.game_display_name = self.game_meta["display_name"]

        self.update_paths(self.get_game_path())

    def update_paths(self, game_path):
        installation_type, self.shipping_exe = self.get_shipping_exe(game_path)

        self.vanilla_files = []
        self.mods_path = None

        self.vanilla_files = [
            {
                "archive": Path(game_path) / suffix,
                "unpacked": (
                    Path(TOOLS["tools_base"]) / "unpacked_vanilla" / Path(suffix).stem
                ).with_suffix(""),
                # "unpacked": (Path(game_path) / suffix.stem).with_suffix(""),
            }
            for suffix in self.game_meta["installations"][installation_type][
                "vanilla_archives_suffixes"
            ]
        ]

        self.mods_path = (
            Path(game_path)
            / self.game_meta["installations"][installation_type]["mods_path_suffix"]
        )

    def get_shipping_exe(self, game_path):
        game_path = Path(game_path)
        for installation_type, installation_data in self.game_meta[
            "installations"
        ].items():
            shipping_exe_suffix = installation_data.get("shipping_exe_suffix")
            if Files.is_existing_file(game_path / shipping_exe_suffix):
                return installation_type, game_path / shipping_exe_suffix
        return "steam", game_path / shipping_exe_suffix  # return steam as default

    def get_game_path(self):
        if steam_path := self.find_steam_game_path(
            self.game_meta["installations"]["steam"]["steam_id"]
        ):
            steam_path = str(Path(steam_path))
            log.debug(f"Steam installation found: {steam_path}")
            return steam_path

        if game_pass_path := self.find_game_pass_game_path(
            self.game_meta["installations"]["game_pass"]["game_folder_name"]
        ):
            game_pass_path = str(Path(game_pass_path))
            log.debug(f"Game Pass installation found: {game_pass_path}")
            return game_pass_path

        fallback_path = str(Path(self.game_meta["fallback_path"]))
        log.debug(f"No installation found, using fallback path: {fallback_path}")
        return fallback_path

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

    def find_game_pass_game_path(self, game_folder_name):

        if not sys.platform.startswith("win"):
            return None

        folder_name = Path("XboxGames") / game_folder_name
        for drive_letter in "CDEFGHIJKLMNOPQRSTUVWXYZ":
            drive = Path(f"{drive_letter}:/")
            potential_path = Path(str(Path(drive / folder_name)))
            if potential_path.exists():
                return str(potential_path)
        return None

    def get_aes_key(self, game_id):
        log.debug("Game Pass installation detection isn't implemented.")
        return None


settings = SettingsManager()
