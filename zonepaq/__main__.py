import os
import platform
import sys

import requests
from backend.logger import log
from backend.utilities import Files
from config.metadata import APP_REPO, APP_URL, APP_VERSION
from config.settings import SettingsManager
from gui.window_first_launch import WindowFirstLaunch
from gui.window_main import WindowMain
from packaging import version

# Get SettingsManager class
settings = SettingsManager()


def get_system_info():
    log.debug("=" * 50)
    log.debug("       System info")
    log.debug("=" * 50)

    # Operating System
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
    log.debug(f"Operating System   : {os_name}")

    # OS Version
    try:
        os_version = platform.version()
    except Exception as e:
        os_version = "Unknown"
    log.debug(f"OS Version         : {os_version}")

    # Machine Type
    try:
        machine_type = platform.machine()
    except Exception as e:
        machine_type = "Unknown"
    log.debug(f"Machine Type       : {machine_type}")

    # Processor
    try:
        processor = platform.processor()
    except Exception as e:
        processor = "Unknown"
    log.debug(f"Processor          : {processor}")

    # Python Version
    try:
        python_version = platform.python_version()
    except Exception as e:
        python_version = "Unknown"
    log.debug(f"Python Version     : {python_version}")

    # Python Build
    try:
        python_build = platform.python_build()
    except Exception as e:
        python_build = "Unknown"
    log.debug(f"Python Build       : {python_build}")

    # Platform Details
    try:
        platform_details = platform.platform()
    except Exception as e:
        platform_details = "Unknown"
    log.debug(f"Platform           : {platform_details}")

    # Architecture
    try:
        architecture = platform.architecture()[0]
    except Exception as e:
        architecture = "Unknown"
    log.debug(f"Architecture       : {architecture}")

    # Current Directory
    try:
        current_dir = os.getcwd()
    except Exception as e:
        current_dir = "Unknown"
    log.debug(f"Current Directory  : {current_dir}")

    log.debug("=" * 50)


def check_new_release(github_repo, current_version):
    try:
        log.debug(f"Querying {github_repo} Github repo...")
        response = requests.get(
            f"https://api.github.com/repos/{github_repo}/releases/latest"
        )
        response.raise_for_status()
        release_data = response.json()

        latest_release_version = release_data.get("tag_name")
        if latest_release_version:
            try:
                current_version_obj = version.parse(current_version.replace(" ", "-"))
                latest_release_version_obj = version.parse(
                    latest_release_version.replace(" ", "-")
                )

                if latest_release_version_obj > current_version_obj:
                    log.info(f"A newer version {latest_release_version} is available!")
                    return latest_release_version
                else:
                    log.info("You are on the latest version.")
                    return False
            except version.InvalidVersion:
                log.exception(
                    f"Invalid version format: {current_version} or {latest_release_version}"
                )
                return False
        log.warning("Couldn't check the latest version.")
        return False
    except requests.exceptions.RequestException as e:
        log.exception(f"Error fetching release data: {e}")
        return False
    except Exception as e:
        log.exception(f"Unexpected error during version check: {e}")
        return False


def check_for_update():
    update_available = check_new_release(APP_REPO, APP_VERSION)
    if update_available:

        if (
            settings.config.get("SETTINGS")
            and settings.config.get("SETTINGS").get("skip_version")
            and update_available
            == eval(settings.config.get("SETTINGS").get("skip_version"))
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

        print(reply)
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

    if eval(settings.config.get("SETTINGS").get("first_launch")):

        # Delete settings file
        Files.delete_path(settings.INI_SETTINGS_FILE)

        # Reset Settings class
        settings.reset_instance()

        gui = WindowFirstLaunch()
        gui.mainloop()

    check_for_update()

    gui = WindowMain()
    gui.mainloop()

    log.info("Application finished.")
    # sys.exit(0)
