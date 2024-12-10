SETTINGS_FILE = "settings.ini"

DEFAULT_TOOLS_PATHS = {
    "repak_cli": r"C:\Program Files\repak_cli\bin\repak.exe",
    "WinMerge": r"C:\Program Files\WinMerge\WinMergeU.exe",
    "kdiff3": r"C:\Program Files\KDiff3\kdiff3.exe",
}

DEFAULT_SETTINGS = {
    "MERGING_ENGINE": "kdiff3",
    "LANG_NAME": "English",
    "THEME_NAME": "Stalker",
    "SHOW_HINTS": "True",
}

TOOL_LINKS = {
    "REPAK_LINK": "https://github.com/trumank/repak/releases",
    "WINMERGE_LINK": "https://winmerge.org",
    "KDIFF3_LINK": "https://kdiff3.sourceforge.io",
}

DEFAULT_GAME = "S.T.A.L.K.E.R. 2"
DEFAULT_VANILLA_FOLDER_SUFFIX = r"Stalker2\Content\Paks\pakchunk0-Windows"

GAMES = {
    "S.T.A.L.K.E.R. 2": {
        "steam_id": "1643320",
        "fallback_path": r"C:\Program Files (x86)\Steam\steamapps\common\S.T.A.L.K.E.R. 2 Heart of Chornobyl",
    },
}
