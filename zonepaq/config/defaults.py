from pathlib import Path

from backend.tools import Files


TOOLS = {
    "tools_base": Path("zonepaq/tools"),
    "7zr": {
        "display_name": "7zr",
        "direct_link": "https://7-zip.org/a/7zr.exe",
        "exe_name": "7zr.exe",
        "local_exe": Path("zonepaq/tools/7zr/7zr.exe"),
    },
    "repak_cli": {
        "display_name": "repak cli",
        "github_repo": "trumank/repak",
        "exe_name": "repak.exe",
        "asset_regex": r"repak_cli-x86_64-pc-windows-msvc.zip$",
        "extract_parameter": "",
        "local_exe": Path("zonepaq/tools/repak_cli/repak.exe"),
        "fallback_exe": Path("C:/Program Files/repak_cli/bin/repak.exe"),
    },
    "kdiff3": {
        "display_name": "KDiff3",
        "base_url": "https://download.kde.org/stable/kdiff3/",
        "exe_name": "kdiff3.exe",
        "extract_parameter": "bin",
        "local_exe": Path("zonepaq/tools/KDiff3/kdiff3.exe"),
        "winreg_path": r"SOFTWARE\KDiff3",
        "fallback_exe": Path("C:/Program Files/KDiff3/kdiff3.exe"),
    },
    "winmerge": {
        "display_name": "WinMerge",
        "github_repo": "winmerge/winmerge",
        "exe_name": "WinMergeU.exe",
        "asset_regex": r"winmerge-\d+(\.\d+)*-exe.zip$",
        "extract_parameter": "WinMerge",
        "local_exe": Path("zonepaq/tools/WinMerge/WinMergeU.exe"),
        "fallback_exe": Path.home() / "AppData/Local/Programs/WinMerge/WinMergeU.exe",
    },
    "aes_dumpster": {
        "display_name": "AESDumpster",
        "github_repo": "GHFear/AESDumpster",
        "exe_name": "AESDumpster-Win64.exe",
        "asset_regex": r"AESDumpster-Win64.exe$",
        "local_exe": Path("zonepaq/tools/AESDumpster/AESDumpster-Win64.exe"),
    },
}

SUPPORTED_MERGING_ENGINES = {
    "kdiff3": {"name": TOOLS["kdiff3"]["display_name"]},
    "winmerge": {"name": TOOLS["winmerge"]["display_name"]},
}

DEFAULT_TOOLS_PATHS = {
    "repak_cli": Files.find_app_installation(
        exe_name=TOOLS["repak_cli"]["exe_name"],
        local_exe=TOOLS["repak_cli"]["local_exe"],
        fallback_exe=TOOLS["repak_cli"]["fallback_exe"],
    ),
    "kdiff3": Files.find_app_installation(
        exe_name=TOOLS["kdiff3"]["exe_name"],
        local_exe=TOOLS["kdiff3"]["local_exe"],
        winreg_path=TOOLS["kdiff3"]["winreg_path"],
        fallback_exe=TOOLS["kdiff3"]["fallback_exe"],
    ),
    "winmerge": Files.find_app_installation(
        exe_name=TOOLS["winmerge"]["exe_name"],
        local_exe=TOOLS["winmerge"]["local_exe"],
        fallback_exe=TOOLS["winmerge"]["fallback_exe"],
    ),
    "aes_dumpster": TOOLS["aes_dumpster"]["local_exe"],
}

DEFAULT_SETTINGS = {
    "merging_engine": "KDiff3",
    "lang_name": "English",
    "theme_name": "Nord",
    "dark_mode": "True",
    "show_hints": "True",
    "aes_key": "0x33A604DF49A07FFD4A4C919962161F5C35A134D37EFA98DB37A34F6450D7D386",
}


DEFAULT_GAME = "S.T.A.L.K.E.R. 2"
DEFAULT_VANILLA_FOLDER_SUFFIX = str(Path("Stalker2/Content/Paks/pakchunk0-Windows"))

GAMES = {
    "S.T.A.L.K.E.R. 2": {
        "steam_id": "1643320",
        "fallback_path": str(
            Path(
                "C:/Program Files (x86)/Steam/steamapps/common/S.T.A.L.K.E.R. 2 Heart of Chornobyl"
            )
        ),
    },
}
