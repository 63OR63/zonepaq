import re
from pathlib import Path
import shutil
import sys

from backend.logger import log


class Files:
    """Utility class for files/folders analysis and management."""

    @staticmethod
    def get_base_path():
        try:
            base_path = Path(sys._MEIPASS)
        except Exception:
            base_path = Path(".")
        return base_path

    @classmethod
    def is_existing_folder(cls, folder_path):
        try:
            folder = Path(folder_path).resolve()
            if not folder.is_dir():
                log.debug(f"{str(folder)} folder doesn't exist.")
                return False
            if folder in {Path(".").resolve(), Path("/").resolve()}:
                log.debug(f"{str(folder)} folder is located at wrong location.")
                return False
            log.debug(f"{str(folder)} folder exists.")
            return True
        except Exception as e:
            log.exception(f"Error during folder path validation: {e}")
            return False

    @classmethod
    def is_existing_file(cls, file_path):
        try:
            file = Path(file_path).resolve()
            if file.exists() and file.is_file():
                log.debug(f"{str(file)} file exists.")
                return True
            log.debug(f"{str(file)} file doesn't exist.")
            return False
        except Exception as e:
            log.exception(f"Error during file path validation: {e}")
            return False

    @classmethod
    def is_existing_file_type(cls, file_path, file_type):
        try:
            file = Path(file_path).resolve()
            if cls.is_existing_file(file_path) and file.suffix.lower() == file_type:
                log.debug(f"{str(file)} extension is {str(file_type)}")
                return True
            log.debug(f"{str(file)} extension isn't {str(file_type)}")
            return False
        except Exception as e:
            log.exception(f"Error during file path validation: {e}")
            return False

    @classmethod
    def is_folder_empty(cls, folder_path):
        try:
            folder = Path(folder_path).resolve()
            if cls.is_existing_folder(folder_path):
                if not any(item.is_file() for item in folder.rglob("*")):
                    log.debug(f"{str(folder)} is empty.")
                    return True
            else:
                return True
            log.debug(f"{str(folder)} isn't empty.")
            return False
        except Exception as e:
            log.exception(f"Error during folder content validation: {e}")
            return False

    @staticmethod
    def delete_path(path):
        try:
            path = Path(path).resolve()
            if not path.exists():
                return False
            if path.is_dir():
                shutil.rmtree(path)
                log.debug(f"Deleted folder: {str(path)}")
                return True
            else:
                path.unlink()
                log.debug(f"Deleted file: {str(path)}")
                return True
        except Exception as e:
            log.exception(f"Deletion failed for {str(path)}: {e}")
            return False

    @staticmethod
    def get_relative_path(path):
        resolved_path = Path(path).resolve()
        try:
            relative_path = resolved_path.relative_to(Path.cwd())
            return str(relative_path)
        except ValueError:
            return str(resolved_path)

    @classmethod
    def copy_folder_contents(cls, source_folder, destination_folder):
        try:
            source_path = Path(source_folder)
            destination_path = Path(destination_folder)

            # Validate source folder
            if not cls.is_existing_folder(source_path):
                raise FileNotFoundError(
                    f"Source folder '{source_folder}' does not exist or is invalid."
                )

            # Ensure the destination folder exists
            destination_path.mkdir(parents=True, exist_ok=True)

            # Copy contents of the source folder to the destination folder
            for item in source_path.iterdir():
                destination_item = destination_path / item.name

                if item.is_dir():
                    shutil.copytree(item, destination_item, dirs_exist_ok=True)
                else:
                    shutil.copy2(item, destination_item)

            log.debug(
                f"All contents copied from '{source_folder}' to '{destination_folder}'."
            )

        except Exception as e:
            log.exception(f"Error during folder copy operation: {e}")

    @staticmethod
    def find_app_installation(
        exe_name, local_exe=None, winreg_path=None, winreg_key="", fallback_exe=None
    ):
        if sys.platform != "win32":
            exe_name = Path(exe_name).stem
            local_exe = Path(local_exe).with_suffix("")

        # 1. Check for local installation
        if local_exe:
            local_exe = Path(local_exe)
            if local_exe.exists():
                log.debug(f"{exe_name} found: {str(local_exe)}")
                return str(local_exe)

        # 2. Check if app is in system PATH
        if env_exe := shutil.which(exe_name):
            log.debug(f"{exe_name} found: {str(Path(env_exe))}")
            return str(Path(env_exe))

        # 3. Check in Windows Registry
        if winreg_path and sys.platform == "win32":
            try:
                import winreg

                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, winreg_path) as key:
                    install_dir, _ = winreg.QueryValueEx(key, winreg_key)
                    winreg_exe = Path(install_dir) / exe_name
                    if winreg_exe.exists():
                        log.debug(f"{exe_name} found in Registry: {str(winreg_exe)}")
                        return str(winreg_exe)
            except (FileNotFoundError, OSError):
                log.warning(
                    f"{exe_name} not found in the Windows Registry at {winreg_path}."
                )

        # 4. Fallback to default path
        if fallback_exe:
            log.debug(f"Using default {exe_name} path: {str(fallback_exe)}")
            return str(fallback_exe)

        log.warning(f"No path for {exe_name} was found!")
        return ""

    @staticmethod
    def delete_unwanted_files(folder_path, allowed_extensions):
        folder = Path(folder_path)
        for file_path in folder.rglob("*"):
            if file_path.is_file():
                file_extension = file_path.suffix.lower()
                if file_extension not in allowed_extensions:
                    try:
                        file_path.unlink()
                        # log.debug(f"Deleted: {file_path}")
                    except Exception as e:
                        # log.debug(f"Failed to delete {file_path}: {e}")
                        pass


class Data:
    """Utility class for data analysis."""

    @staticmethod
    def is_valid_data(data, data_type=None):
        try:
            if data_type == "aes":
                if Data.is_valid_aes_key(data):
                    return True
                else:
                    return False
            elif data_type == "folder":
                if Files.is_existing_folder(data):
                    return True
                else:
                    return False
            else:
                if Files.is_existing_file(data):
                    return True
                else:
                    return False
        except Exception as e:
            log.exception(f"Error during data validation: {e}")
            return False

    @staticmethod
    def is_valid_aes_key(key):
        valid_lengths = {16, 24, 32}

        try:
            key = str(key).strip()

            if key.startswith(("0X", "0x")):
                key = key[2:]

            if not re.fullmatch(r"[0-9A-F]+", key):
                log.warning(f"{key} isn't a valid AES key")
                return False

            key_bytes = bytes.fromhex(key)

            log.debug(f"{key} is a valid AES key")
            return len(key_bytes) in valid_lengths

        except Exception as e:
            log.exception(f"Error during AES validation of {key}: {e}")
            return False

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
