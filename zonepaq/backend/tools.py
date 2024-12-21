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
            path = Path(path)
            if not path.exists():
                return False
            if path.is_dir():
                shutil.rmtree(path)
                log.debug(f"Deleted folder: {path}")
                return True
            else:
                path.unlink()
                log.debug(f"Deleted file: {path}")
                return True
        except Exception as e:
            log.error(f"Deletion failed for {path}: {e}")
            return False


class Data:
    """Utility class for data analysis."""

    @staticmethod
    def is_valid_data(data, data_type):
        try:
            if data_type == "aes":
                if Data.is_valid_aes_key(data):
                    log.debug(f"{data} is a valid AES key")
                    return True
                else:
                    log.debug(f"{data} isn't a valid AES key")
                    return False
            elif data_type == "folder":
                if Files.is_existing_folder(data):
                    log.debug(f"{data} is an existing folder")
                    return True
                else:
                    return False
            elif Files.is_existing_file(data):
                is_windows = sys.platform == "win32"
                if (is_windows and Path(data).name == f"{data_type}.exe") or Path(
                    data
                ).stem == data_type:
                    log.debug(f'{data} is a valid path to "{data_type}"')
                    return True
                else:
                    log.warning(f'{data} isn\'t a valid path to "{data_type}"')
                    return False
            else:
                log.warning(f'{data} isn\'t a valid "{data_type}"')
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
                return False

            key_bytes = bytes.fromhex(key)

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
