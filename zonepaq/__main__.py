import os
import platform
from distutils.util import strtobool

import requests
from backend.logger import log
from backend.utilities import Files
from config.metadata import APP_REPO, APP_URL, APP_VERSION
from config.settings_manager import settings
from gui.window_first_launch import WindowFirstLaunch
from gui.window_main import WindowMain
from packaging import version


def get_system_info():
    log.info("=" * 50)
    log.info("       System info")
    log.info("=" * 50)

    def get_operating_system():
        try:
            if platform.system() == "Windows":
                os_version = platform.version()
                if os_version.startswith("10.0"):
                    build_number = int(os_version.split(".")[2])
                    if build_number >= 22000:
                        os_name = "Windows 11"
                    else:
                        os_name = "Windows 10"
                else:
                    os_name = f"Windows (Unknown Version: {os_version})"
            else:
                os_name = f"{platform.system()} {platform.release()}"
        except Exception:
            os_name = "Unknown"
        return os_name

    system_info = {
        "Operating System": get_operating_system(),
        "OS Version": platform.version(),
        "Machine Type": platform.machine(),
        "Processor": platform.processor(),
        "Python Version": platform.python_version(),
        "Python Build": platform.python_build(),
        "Platform": platform.platform(),
        "Architecture": platform.architecture()[0],
        "Current Directory": os.getcwd(),
    }

    for key, value in system_info.items():
        log.info(f"{key:<20}: {value or 'Unknown'}")
    log.info("=" * 50)


def check_new_release(github_repo, current_version):
    headers = {"Accept": "application/vnd.github.v3+json"}
    try:
        log.debug(f"Querying {github_repo} Github repo...")
        response = requests.get(
            f"https://api.github.com/repos/{github_repo}/releases/latest",
            headers=headers,
        )
        response.raise_for_status()
        release_data = response.json()

        latest_release_version = release_data.get("tag_name")
        if not latest_release_version:
            log.warning("No release version found in API response.")
            return False

        current_version_obj = version.parse(current_version)
        latest_version_obj = version.parse(latest_release_version)

        if latest_version_obj > current_version_obj:
            log.info(f"Newer version {latest_release_version} available.")
            return latest_release_version

        log.info("You are on the latest version.")
        return False
    except requests.exceptions.RequestException as e:
        log.error(f"API error: {e}")
        return False


def check_for_update():
    update_available = check_new_release(APP_REPO, APP_VERSION)
    if update_available:

        if (
            settings.config.get("SETTINGS")
            and settings.config.get("SETTINGS").get("skip_version")
            and update_available == settings.config.get("SETTINGS").get("skip_version")
        ):
            log.debug(f"Skipping version {update_available}.")
            return None

        from config.translations import translate
        from gui.template_base import TemplateBase
        from gui.window_messagebox import WindowMessageBox

        master = TemplateBase(title="")
        master.withdraw()
        reply = WindowMessageBox.askyesnocancel(
            master,
            translate("generic_question"),
            f'{translate("dialogue_request_update_1")} {update_available} {translate("dialogue_request_update_2")}',
        )
        master.destroy()

        if reply == True:
            import webbrowser

            webbrowser.open(f"{APP_URL}/releases")
            return True
            # sys.exit(0)
        elif reply == False:
            log.debug(f"Skipping update to {update_available}.")
            return False
        elif reply == None:
            log.debug(f"Ignoring version {update_available}.")
            settings.update_config("SETTINGS", "skip_version", str(update_available))
            return False
        return False


if __name__ == "__main__":
    get_system_info()
    log.info("Starting the application...")

    if bool(strtobool(settings.get("SETTINGS", "first_launch"))):

        # Delete settings file
        Files.delete_path(settings.INI_SETTINGS_FILE)

        # Reset Settings class
        settings.initialize()

        gui = WindowFirstLaunch()
        gui.mainloop()

    check_for_update()

    gui = WindowMain()
    gui.mainloop()

    log.info("Application finished.")
    # sys.exit(0)
