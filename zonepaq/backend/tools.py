import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from pathlib import Path

from backend.logger import log
from config.settings import settings

executor = ThreadPoolExecutor()


def run_in_executor(func):
    """Decorator to run methods asynchronously using ThreadPoolExecutor."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        return executor.submit(func, *args, **kwargs)

    return wrapper


class Repak:
    """Provides methods for listing, unpacking, and repacking files using the Repak CLI tool."""

    REPAK_PATH = settings.TOOLS_PATHS["repak_cli"]

    @classmethod
    @run_in_executor
    def get_list(cls, file):
        log.debug(f"Attempting to list contents of the file: {file}")
        try:
            file = Path(file)
            result = subprocess.run(
                [cls.REPAK_PATH, "list", str(file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            if result.returncode != 0:
                log.error(
                    f"Failed to list contents of {str(file)}: {result.stderr.strip()}"
                )
                raise RuntimeError(
                    f"Command failed with error:\n{result.stderr.strip()}"
                )

            log.debug(f"Successfully listed contents of {str(file)}")
            return True, result.stdout.strip().splitlines()
        except Exception as e:
            log.exception(
                f"An error occurred while listing the contents of {str(file)}"
            )
            return False, str(e)

    @classmethod
    @run_in_executor
    def unpack(cls, source, destination):
        log.debug(f"Attempting to unpack: {source}")
        try:
            source = Path(source)
            destination = Path(destination)
            unpacked_folder = Path(source).with_suffix("")

            if unpacked_folder.is_dir():
                log.warning(f"Removing existing unpacked folder: {unpacked_folder}")
                shutil.rmtree(unpacked_folder)

            result = subprocess.run(
                [cls.REPAK_PATH, "unpack", str(source)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                log.error(f"Failed to unpack {source}: {result.stderr.strip()}")
                raise RuntimeError(
                    f"Command failed with error:\n{result.stderr.strip()}"
                )

            target_folder = destination / unpacked_folder.name

            if target_folder.is_dir():
                log.warning(f"Removing existing target folder: {str(target_folder)}")
                shutil.rmtree(target_folder)

            shutil.move(unpacked_folder, target_folder)
            log.info(f"Successfully unpacked {str(source)} to {str(target_folder)}")
            return True, str(target_folder)

        except Exception as e:
            log.exception(f"An error occurred while unpacking {str(source)}")
            return False, str(e)

    @classmethod
    @run_in_executor
    def repack(cls, source, destination=None, forced_destination=None):
        if not destination and not forced_destination:
            raise TypeError(
                "repack() missing required arguments: either 'destination' or 'forced_destination'"
            )
        log.debug(f"Attempting to repack: {source}")
        try:
            source = Path(source)

            if forced_destination:
                packed_file = Path(forced_destination)
            else:
                packed_file = Path(destination) / f"{source.name}.pak"

            if packed_file.is_file():
                log.warning(f"Removing existing packed file: {packed_file}")
                packed_file.unlink()

            result = subprocess.run(
                [
                    cls.REPAK_PATH,
                    "pack",
                    "--version",
                    "V11",
                    str(source),
                    str(packed_file),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                log.error(f"Failed to repack {str(source)} to {str(packed_file)}")
                raise RuntimeError(
                    f"Command failed with error:\n{result.stderr.strip()}"
                )

            log.info(f"Successfully repacked {str(source)} to {str(packed_file)}")
            return True, str(packed_file)

        except Exception as e:
            log.exception(f"An error occurred while repacking {str(source)}")
            return False, str(e)


class Merging:
    """Provides methods for merging engines."""

    @staticmethod
    def _run_engine(unpacked_files, save_path):

        merging_engine = settings.MERGING_ENGINE
        tool_paths = settings.TOOLS_PATHS

        save_path = Path(save_path)
        unpacked_files_paths = [Path(f) for f in unpacked_files]

        if merging_engine == "WinMerge":
            engine_path = Path(tool_paths.get("winmerge"))
            if not engine_path.exists():
                log.error(f"{merging_engine} doesn't exist at {engine_path}")
                return False, None
            command = [
                str(engine_path),
                "/o",
                str(save_path),
                *map(str, unpacked_files_paths),
            ]
        elif merging_engine == "kdiff3":
            engine_path = Path(tool_paths.get("kdiff3"))
            if not engine_path.exists():
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
            log.error(f"Error during merging: {e}")


class Files:
    """Utility class for folder analysis, content tree building, and duplicate detection."""

    @staticmethod
    def is_folder_empty(folder_path):
        folder = Path(folder_path)
        return not any(item.is_file() for item in folder.rglob("*"))

    @staticmethod
    def build_content_tree(gathered_files: dict) -> dict:
        content_tree = {}
        for source_path, file_paths in gathered_files.items():
            for file_path in file_paths:
                parts = Path(file_path).parts
                game_name, *file_hierarchy, file_name = parts

                current_level = content_tree.setdefault(game_name, {})
                for part in file_hierarchy:
                    current_level = current_level.setdefault(part, {})

                current_level.setdefault(file_name, []).append(source_path)

        return content_tree
