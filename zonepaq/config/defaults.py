from pathlib import Path
import shutil
import sys

from backend.logger import log


def check_app_installed(
    app_exe, local_path=None, winreg_path=None, winreg_key="", default_path=""
):
    if sys.platform == "win32":
        app_exe = f"{app_exe}.exe"

    # 1. Check for local installation
    if local_path:
        local_path = Path(local_path) / app_exe
        if local_path.exists():
            log.debug(
                f"{app_exe} found in zonepaq/tools/{local_path}: {str(local_path)}"
            )
            return str(local_path)

    # 2. Check if app is in system PATH
    if path := shutil.which(app_exe):
        log.debug(f"{app_exe} found: {str(Path(path))}")
        return str(Path(path))

    # 3. Check in Windows Registry
    if winreg_path and sys.platform == "win32":
        try:
            import winreg

            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, winreg_path) as key:
                install_dir, _ = winreg.QueryValueEx(key, winreg_key)
                path = Path(install_dir) / app_exe
                if path.exists():
                    log.debug(f"{app_exe} found in Registry: {str(path)}")
                    return str(path)
        except (FileNotFoundError, OSError):
            log.warning(
                f"{app_exe} not found in the Windows Registry at {winreg_path}."
            )

    # 4. Fallback to default path
    default_path = str(Path(default_path) / app_exe)
    log.debug(f"Using default {app_exe} path: {default_path}")
    return default_path


TOOLS = {
    "tools_base": Path("zonepaq/tools"),
    "7zr": {
        "direct_link": "https://7-zip.org/a/7zr.exe",
        "exe": "7zr",
    },
    "repak_cli": {
        "github_repo": "trumank/repak",
        "exe": "repak",
    },
    "kdiff3": {
        "base_url": "https://download.kde.org/stable/kdiff3/",
        "exe": "kdiff3",
    },
    "winmerge": {
        "github_repo": "winmerge/winmerge",
        "exe": "WinMergeU",
    },
}

SUPPORTED_MERGING_ENGINES = {
    "kdiff3": {"name": "KDiff3"},
    "winmerge": {"name": "WinMerge"},
}

DEFAULT_TOOLS_PATHS = {
    "repak_cli": check_app_installed(
        app_exe=TOOLS["repak_cli"]["exe"],
        local_path=TOOLS["tools_base"] / "repak_cli",
        default_path=r"C:\Program Files\repak_cli\bin",
    ),
    "kdiff3": check_app_installed(
        app_exe=TOOLS["kdiff3"]["exe"],
        local_path=TOOLS["tools_base"] / "KDiff3",
        winreg_path=r"SOFTWARE\KDiff3",
        default_path=r"C:\Program Files\KDiff3",
    ),
    "winmerge": check_app_installed(
        app_exe=TOOLS["winmerge"]["exe"],
        local_path=TOOLS["tools_base"] / "WinMerge",
        default_path=Path.home() / "AppData" / "Local" / "Programs" / "WinMerge",
    ),
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
DEFAULT_VANILLA_FOLDER_SUFFIX = r"Stalker2\Content\Paks\pakchunk0-Windows"

GAMES = {
    "S.T.A.L.K.E.R. 2": {
        "steam_id": "1643320",
        "fallback_path": r"C:\Program Files (x86)\Steam\steamapps\common\S.T.A.L.K.E.R. 2 Heart of Chornobyl",
    },
}
