import subprocess
from pathlib import Path

from backend.logger import log
from backend.utilities import Files
from config.settings import SettingsManager

# Get SettingsManager class
settings = SettingsManager()


class Merging:
    """Provides methods for merging engines."""

    @staticmethod
    def _run_engine(unpacked_files, save_path):

        merging_engine = settings.MERGING_ENGINE
        tool_paths = settings.TOOLS_PATHS

        save_path = Path(save_path)
        unpacked_files_paths = [Path(f) for f in unpacked_files]

        #! add /self-compare /wl if only one file is going to open
        # https://manual.winmerge.org/en/Command_line.html
        if merging_engine == "WinMerge":
            engine_path = Path(tool_paths.get("winmerge"))
            if not Files.is_existing_file_type(engine_path, ".exe"):
                log.error(f"{merging_engine} doesn't exist at {engine_path}")
                return False, None
            command = [str(engine_path), "/wl"]
            if len(unpacked_files_paths) == 1:
                command += ["/self-compare"]
            if len(unpacked_files_paths) == 3:
                command += ["/wm"]
            command += [
                "/o",
                str(save_path),
                *map(str, unpacked_files_paths),
            ]

        elif merging_engine == "KDiff3":
            engine_path = Path(tool_paths.get("KDiff3"))
            if not Files.is_existing_file_type(engine_path, ".exe"):
                log.error(f"{merging_engine} doesn't exist at {engine_path}")
                return False, None
            command = [
                str(engine_path),
                "-o",
                str(save_path),
                *map(str, unpacked_files_paths),
            ]
        else:
            log.error(f"Unsupported merging engine: {merging_engine}")
            return False, None

        try:
            return True, subprocess.run(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
        except FileNotFoundError as e:
            log.error(f"Merging tool not found: {e}")
        except Exception as e:
            log.exception(f"Error during merging: {e}")
