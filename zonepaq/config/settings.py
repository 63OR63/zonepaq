from abc import ABC, abstractmethod
from pathlib import Path

from backend.logger import log
from config.defaults import (
    DEFAULT_SETTINGS,
    DEFAULT_TOOLS_PATHS,
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


class SettingsManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.init()
        return cls._instance

    @classmethod
    def reset_instance(cls):
        cls._instance = None

    @classmethod
    def init(cls):
        cls.INI_SETTINGS_FILE = r"zonepaq\settings.ini"
        Path(cls.INI_SETTINGS_FILE).parent.mkdir(parents=True, exist_ok=True)

        sources = [
            IniConfigSource(cls.INI_SETTINGS_FILE),
        ]

        from backend.games_manager import GamesManager

        games_manager = GamesManager()

        defaults = {
            "SETTINGS": DEFAULT_SETTINGS,
            "TOOLS_PATHS": DEFAULT_TOOLS_PATHS,
            "GAME_PATHS": {games_manager.game_name: str(Path(games_manager.game_path))},
        }

        cls.loader = ConfigurationLoader(sources, defaults)

        cls.config = cls.loader.load()

        cls.load()

    @classmethod
    def load(cls):
        cls.MERGING_ENGINE = cls.get("SETTINGS", "merging_engine")
        cls.LANG_NAME = cls.get("SETTINGS", "lang_name")
        cls.THEME_NAME = cls.get("SETTINGS", "theme_name")
        cls.SHOW_HINTS = cls.get("SETTINGS", "show_hints")
        cls.DARK_MODE = cls.get("SETTINGS", "dark_mode")
        cls.AES_KEY = cls.get("SETTINGS", "aes_key")
        cls.TOOLS_PATHS = cls.get("TOOLS_PATHS")
        cls.GAME_PATHS = cls.get("GAME_PATHS")
        cls.LANG_DICT = get_translation(cls.LANG_NAME)
        cls.ALL_LANG_NAMES = get_available_languages()
        cls.ALL_THEME_NAMES = ThemeManager.get_available_theme_names()
        cls.SUPPORTED_MERGING_ENGINES = [
            engine["name"] for engine in SUPPORTED_MERGING_ENGINES.values()
        ]
        cls.TOOLS = TOOLS

    @classmethod
    def update_config(cls, section, key, value):
        cls.set(section, key, value)
        cls.save()
        cls.load()

    @classmethod
    def set(cls, section, key, value):
        cls.config[section][key] = str(value)

    @classmethod
    def get(cls, section, key=None):
        if key is None:
            return cls.config.get(section)
        return cls.config.get(section).get(key)

    @classmethod
    def save(cls):
        cls.loader.save(cls.config)
