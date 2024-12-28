from pathlib import Path
import sys


WORKING_DIR = Path(__file__).resolve().parent.parent

if str(WORKING_DIR) not in sys.path:
    sys.path.insert(0, str(WORKING_DIR))

from zonepaq.config import metadata

from zonepaq.config.translations import TRANSLATIONS


def find_missing_keys(translations):

    english_translations = translations.get("English", {})
    russian_keys = set(translations.get("Русский", {}).keys())

    missing_translations = {
        key: value
        for key, value in english_translations.items()
        if key not in russian_keys
    }

    return missing_translations


missing_translations = find_missing_keys(TRANSLATIONS)
print(missing_translations)
