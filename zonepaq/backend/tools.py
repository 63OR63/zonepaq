import re
from pathlib import Path

from backend.logger import log


class Files:
    """Utility class for folder analysis, content tree building, and duplicate detection."""

    @staticmethod
    def is_existing_folder(folder_path):
        try:
            folder = Path(folder_path)

            path_str = str(folder).strip("/")
            if not path_str:
                return False
            if set(path_str) == {"."}:
                return False
            resolved_path = folder.resolve()
            if resolved_path in {Path(".").resolve(), Path("/").resolve()}:
                return False

            return folder.exists() and folder.is_dir()
        except Exception as e:
            log.exception(f"Error during folder path validation: {e}")
            return False

    @staticmethod
    def is_existing_file_type(file_path, file_type):
        try:
            file = Path(file_path)
            return file.exists() and file.is_file() and file.suffix.lower() == file_type
        except Exception as e:
            log.exception(f"Error during file path validation: {e}")
            return False

    @staticmethod
    def is_folder_empty(folder_path):
        try:
            folder = Path(folder_path)
            if Files.is_existing_folder(folder):
                return not any(item.is_file() for item in folder.rglob("*"))
        except Exception as e:
            log.exception(f"Error during folder content validation: {e}")
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


class Data:
    """Utility class for data analysis."""

    @staticmethod
    def is_valid_data(data, data_type):
        try:
            if data_type == "aes" and Data.is_valid_aes_key(data):
                log.debug(f"{data} is a valid AES key")
                return True
            elif data_type == "folder" and Files.is_existing_folder(data):
                log.debug(f"{data} is an existing folder")
                return True
            elif Files.is_existing_file_type(data, data_type):
                log.debug(f'{data} is an existing "{data_type}" file')
                return True
            else:
                log.warning(f'{data} is an invalid "{data_type}"')
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
