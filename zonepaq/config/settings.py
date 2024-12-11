import re
from configparser import ConfigParser
from pathlib import Path

from .defaults import (
    DEFAULT_GAME,
    DEFAULT_SETTINGS,
    DEFAULT_TOOLS_PATHS,
    DEFAULT_VANILLA_FOLDER_SUFFIX,
    GAMES,
    SETTINGS_FILE,
)
from .themes import get_available_theme_names, get_theme_dict
from .translations import get_available_languages, get_translation


# Subclassing ConfigParser to preserve case
# class CaseSensitiveConfigParser(ConfigParser):
#     def optionxform(self, optionstr):
#         return optionstr


class SteamGameUtils:
    """Utility class for locating Steam game installation paths."""

    @staticmethod
    def find_steam_game_path(game_id):
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

    @staticmethod
    def get_game_path(game_name, games_dict):
        game_details = games_dict.get(game_name)
        steam_id = game_details.get("steam_id")
        fallback_path = game_details.get("fallback_path")
        found_path = SteamGameUtils.find_steam_game_path(steam_id)
        game_path = found_path if found_path is not None else fallback_path
        return game_path


class Settings:
    """Manages application settings."""

    def __init__(self):
        self._reload_settings()
        self.save_settings()

    def _reload_settings(self):
        self.config = self._load_config()
        self.MERGING_ENGINE = self.config["SETTINGS"]["MERGING_ENGINE"]
        self.LANG_NAME = self.config["SETTINGS"]["LANG_NAME"]
        self.THEME_NAME = self.config["SETTINGS"]["THEME_NAME"]
        self.SHOW_HINTS = self.config["SETTINGS"]["SHOW_HINTS"]
        self.AES_KEY = self.config["SETTINGS"]["AES_KEY"]
        self.GAME_PATHS = self.config["GAME_PATHS"]
        self.TOOLS_PATHS = self.config["TOOLS_PATHS"]
        self.LANG_DICT = get_translation(self.LANG_NAME)
        self.THEME_DICT = get_theme_dict(self.THEME_NAME)
        self.ALL_LANG_NAMES = get_available_languages()
        self.ALL_THEME_NAMES = get_available_theme_names()
        self.save_settings()

    def _get_config_value(self, section, key, default):
        return self.config[section].get(key, default)

    def update_config(self, section, key, value):
        self.config[section][key] = str(value)
        self.save_settings()
        self._reload_settings()

    @staticmethod
    def _load_config():
        # config = CaseSensitiveConfigParser()
        config = ConfigParser()
        if Path(SETTINGS_FILE).exists():
            config.read(SETTINGS_FILE)
        config.setdefault("SETTINGS", DEFAULT_SETTINGS)
        config.setdefault("TOOLS_PATHS", DEFAULT_TOOLS_PATHS)
        game_path = SteamGameUtils.get_game_path(DEFAULT_GAME, GAMES)
        vanilla_unpacked = str(Path(game_path) / Path(DEFAULT_VANILLA_FOLDER_SUFFIX))
        game_paths = {"vanilla_unpacked": vanilla_unpacked}
        config.setdefault("GAME_PATHS", game_paths)
        return config

    def save_settings(self):
        with open(SETTINGS_FILE, "w") as configfile:
            self.config.write(configfile)


settings = Settings()


def translate(text, lang=None):
    if lang:
        try:
            return get_translation(lang).get(text) or get_translation("English").get(
                text
            )
        except:
            return get_translation("English").get(text)
    return settings.LANG_DICT.get(text) or get_translation("English").get(text)
