from abc import ABC, abstractmethod
from pathlib import Path

from backend.logger import log
from backend.steam import SteamGameUtils
from config.defaults import (
    DEFAULT_GAME,
    DEFAULT_SETTINGS,
    DEFAULT_TOOLS_PATHS,
    DEFAULT_VANILLA_FOLDER_SUFFIX,
    GAMES,
    TOOLS,
    SUPPORTED_MERGING_ENGINES,
)
from config.themes import ThemeManager
from config.translations import get_available_languages, get_translation


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


class Settings:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, sources, defaults):
        self.loader = ConfigurationLoader(sources, defaults)
        self.load()

    def load(self):
        self.config = self.loader.load()
        self.MERGING_ENGINE = self.get("SETTINGS", "merging_engine")
        self.LANG_NAME = self.get("SETTINGS", "lang_name")
        self.THEME_NAME = self.get("SETTINGS", "theme_name")
        self.SHOW_HINTS = self.get("SETTINGS", "show_hints")
        self.AES_KEY = self.get("SETTINGS", "aes_key")
        self.TOOLS_PATHS = self.get("TOOLS_PATHS")
        self.GAME_PATHS = self.get("GAME_PATHS")
        self.LANG_DICT = get_translation(self.LANG_NAME)
        self.ALL_LANG_NAMES = get_available_languages()
        self.ALL_THEME_NAMES = ThemeManager.get_available_theme_names()
        self.SUPPORTED_MERGING_ENGINES = [
            engine["name"] for engine in SUPPORTED_MERGING_ENGINES.values()
        ]
        self.TOOLS = TOOLS

    def update_config(self, section, key, value):
        self.set(section, key, value)
        self.save()
        self.load()

    def set(self, section, key, value):
        self.config[section][key] = str(value)

    def get(self, section, key=None):
        if key is None:
            return self.config.get(section)
        return self.config.get(section).get(key)

    def save(self):
        self.loader.save(self.config)


INI_SETTINGS_FILE = r"zonepaq\settings.ini"
Path(INI_SETTINGS_FILE).parent.mkdir(parents=True, exist_ok=True)

sources = [
    IniConfigSource(INI_SETTINGS_FILE),
]

defaults = {
    "SETTINGS": DEFAULT_SETTINGS,
    "TOOLS_PATHS": DEFAULT_TOOLS_PATHS,
    "GAME_PATHS": {
        "vanilla_unpacked": str(
            Path(SteamGameUtils.get_game_path(DEFAULT_GAME, GAMES))
            / DEFAULT_VANILLA_FOLDER_SUFFIX
        )
    },
}

settings = Settings(sources, defaults)


def translate(text, lang=None):
    # return settings.LANG_DICT[text]  # to debug raise errors
    if lang:
        try:
            return get_translation(lang).get(text) or get_translation("English").get(
                text
            )
        except:
            return get_translation("English").get(text)
    return settings.LANG_DICT.get(text) or get_translation("English").get(text)
