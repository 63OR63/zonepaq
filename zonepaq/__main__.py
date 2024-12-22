from backend.logger import log
from config.settings import settings, translate
from gui.window_first_launch import WindowFirstLaunch
from gui.window_launch_screen import GUI_LaunchScreen

import platform
import os


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


if __name__ == "__main__":
    get_system_info()
    log.debug("Starting the application...")

    if eval(settings.config.get("SETTINGS").get("first_launch")):
        gui = WindowFirstLaunch()
        gui.mainloop()

    gui = GUI_LaunchScreen()
    gui.mainloop()

    log.debug("Application finished.")
