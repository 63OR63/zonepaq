import os
import re
from pathlib import Path
import shutil
import sys
import time
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
                if not any(folder.iterdir()):
                    log.debug(f"{str(folder)} is empty.")
                    return True
            else:
                return True
            log.debug(f"{str(folder)} isn't empty.")
            return False
        except Exception as e:
            log.exception(f"Error during folder content validation: {e}")
            return False

    @classmethod
    def create_dir(cls, path, retries=3, delay=1, timeout=10):
        """
        Create a directory and its parents.
        """
        try:
            path = Path(path).resolve()
            start_time = time.time()

            for attempt in range(1, retries + 2):
                try:
                    path.mkdir(parents=True, exist_ok=True)
                    log.debug(f"Directory created or already exists: {path}")
                    return True
                except Exception as e:
                    log.warning(
                        f"Attempt {attempt} failed to create directory {path}: {e}"
                    )
                    if attempt < retries + 1:
                        time.sleep(cls._calculate_backoff(attempt, delay))
                    else:
                        log.error(
                            f"Failed to create directory after {retries} retries: {path}"
                        )
                        return False

                if time.time() - start_time > timeout:
                    log.error(f"Timeout exceeded while creating directory: {path}")
                    return False

        except Exception as e:
            log.exception(f"Unexpected error during directory creation: {e}")
            return False

    @classmethod
    def copy_folder_contents(
        cls, source_folder, destination_folder, retries=3, delay=1, timeout=10
    ):
        """
        Copy the contents of a folder to a destination folder by reusing `copy_path`.
        """
        try:
            source_path = Path(source_folder).resolve()
            destination_path = Path(destination_folder).resolve()

            # Validate source folder
            if not source_path.is_dir():
                log.error(
                    f"Source folder does not exist or is not a directory: {source_folder}"
                )
                return False

            # Ensure the destination folder exists
            cls.create_dir(destination_path)

            # Iterate over the contents of the source folder
            for item in source_path.iterdir():
                # Set destination for each item
                destination_item = destination_path / item.name

                # Use `copy_path` to handle each item
                if not cls.copy_path(item, destination_item, retries, delay, timeout):
                    return False  # Stop on the first failure

            log.debug(
                f"Successfully copied contents of {source_folder} to {destination_folder}"
            )
            return True

        except Exception as e:
            log.exception(f"Error during folder contents copy: {e}")
            return False

    @classmethod
    def copy_path(cls, src, dest, retries=3, delay=1, timeout=10):
        """
        Copy a file or folder to a destination with retries and error handling.
        """
        try:
            src = Path(src).resolve()
            dest = Path(dest).resolve()

            cls.create_dir(dest.parent)

            if not src.exists():
                log.error(f"Source path does not exist: {src}")
                return False

            start_time = time.time()
            for attempt in range(1, retries + 2):
                try:
                    if src.is_dir():
                        shutil.copytree(src, dest)
                    else:
                        shutil.copy2(src, dest)
                    log.debug(f"Copied {src} to {dest}")
                    return True
                except Exception as e:
                    log.warning(
                        f"Attempt {attempt} failed for copying {src} to {dest}: {e}"
                    )
                    if attempt < retries + 1:
                        time.sleep(cls._calculate_backoff(attempt, delay))
                    else:
                        log.error(
                            f"Failed to copy after {retries} retries: {src} to {dest}"
                        )
                        return False
        except Exception as e:
            log.exception(f"Unexpected error during copy operation: {e}")
            return False

    @classmethod
    def move_path(cls, src, dest, retries=3, delay=1, timeout=10):
        """
        Move a file or folder to a destination with retries and error handling.
        """
        try:
            src = Path(src).resolve()
            dest = Path(dest).resolve()

            cls.create_dir(dest.parent)

            if not src.exists():
                log.error(f"Source path does not exist: {src}")
                return False

            start_time = time.time()
            for attempt in range(1, retries + 2):
                try:
                    shutil.move(str(src), str(dest))
                    log.debug(f"Moved {src} to {dest}")
                    return True
                except Exception as e:
                    log.warning(
                        f"Attempt {attempt} failed for moving {src} to {dest}: {e}"
                    )
                    if attempt < retries + 1:
                        time.sleep(cls._calculate_backoff(attempt, delay))
                    else:
                        log.error(
                            f"Failed to move after {retries} retries: {src} to {dest}"
                        )
                        return False
        except Exception as e:
            log.exception(f"Unexpected error during move operation: {e}")
            return False

    # !WORKAROUND for shutil.rmtree hanging up in some cases
    @classmethod
    def delete_path(cls, path, retries=3, delay=1, timeout=10, allowed_extensions=None):
        """
        Delete a file or folder with retries and enhanced error handling.
        Optionally only delete files not in the allowed_extensions list.
        """
        try:
            path = Path(path).resolve()

            # Check if the path is a root directory or top-level folder
            if path == path.anchor:
                log.warning(
                    f"Operation stopped: Path is a root directory or top-level folder: {str(path)}"
                )
                return False

            # Check for known system folders and their subpaths (e.g., Windows directory)
            system_folders = [
                Path("C:/Windows"),
                Path("C:/Windows/System32"),
            ]
            if any(folder in path.parents for folder in system_folders):
                log.warning(
                    f"Operation stopped: Path is within a system folder: {str(path)}"
                )
                return False

            # Check for specific protected folders on Windows
            protected_folders = [
                Path("C:/Users"),
                Path("C:/Program Files"),
                Path("C:/Program Files (x86)"),
            ]
            if any(path == folder for folder in protected_folders):
                log.warning(
                    f"Operation stopped: Path is a protected folder: {str(path)}"
                )
                return False

            if not path.exists():
                log.debug(f"Path does not exist: {str(path)}")
                return False

            start_time = time.time()
            for attempt in range(1, retries + 2):
                try:
                    if path.is_dir():
                        cls._remove_dir(
                            path,
                            start_time,
                            retries,
                            delay,
                            timeout,
                            allowed_extensions,
                        )
                        log.debug(f"Deleted folder: {str(path)}")
                    else:
                        if cls._should_delete_file(path, allowed_extensions):
                            cls._remove_file(path, start_time, retries, delay, timeout)
                            log.debug(f"Deleted file: {str(path)}")
                    return True
                except Exception as e:
                    log.warning(f"Attempt {attempt} failed for {str(path)}: {e}")
                    if attempt < retries + 1:
                        time.sleep(cls._calculate_backoff(attempt, delay))
                    else:
                        log.error(
                            f"Failed to delete path after {retries} retries: {str(path)}"
                        )
                        return False
        except Exception as e:
            log.exception(f"Unexpected error while resolving path: {e}")
            return False

    @classmethod
    def _remove_dir(cls, path, start_time, retries, delay, timeout, allowed_extensions):
        """
        Manually remove a directory with retries and handling of locked files.
        Only deletes files not in allowed_extensions if the parameter is provided.
        """
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                file_path = Path(root) / name
                if cls._should_delete_file(file_path, allowed_extensions):
                    cls._remove_file(file_path, start_time, retries, delay, timeout)

            for name in dirs:
                dir_path = Path(root) / name
                try:
                    if not any(Path(dir_path).iterdir()):
                        os.rmdir(dir_path)
                except OSError as e:
                    log.warning(f"Could not remove directory {dir_path}: {e}")
                    cls._handle_remove_readonly(os.rmdir, dir_path, e)

        try:
            if not any(path.iterdir()):
                os.rmdir(path)
        except OSError as e:
            log.error(f"Failed to remove directory {path}: {e}")
            cls._handle_remove_readonly(os.rmdir, path, e)

    @classmethod
    def _remove_file(cls, file_path, start_time, retries, delay, timeout):
        """
        Attempt to remove a file with retries.
        """
        for attempt in range(retries):
            try:
                file_path.unlink()
                return
            except PermissionError as e:
                log.warning(f"Permission error removing file {file_path}: {e}")
                cls._handle_remove_readonly(file_path.unlink, file_path, e)
                cls._log_locked_files(file_path)
            except Exception as e:
                log.warning(f"Unexpected error removing file {file_path}: {e}")

            # Break if timeout is exceeded
            if time.time() - start_time > timeout:
                log.error(f"Timeout exceeded while deleting {file_path}")
                break

            time.sleep(delay)
        log.error(f"Failed to remove file after retries: {file_path}")

    @staticmethod
    def _should_delete_file(file_path, allowed_extensions):
        """
        Check if a file should be deleted based on allowed_extensions.
        """
        if allowed_extensions is None:
            return True

        allowed_extensions = {ext.lower() for ext in allowed_extensions}

        return file_path.suffix.lower() not in allowed_extensions

    @staticmethod
    def _handle_remove_readonly(func, path, exc_info):
        """
        Handle readonly file removal errors by changing permissions and retrying.
        """
        import stat

        if not os.access(path, os.W_OK):
            os.chmod(path, stat.S_IWUSR)
            try:
                func(path)
            except Exception as e:
                log.error(f"Failed to remove {path} after chmod: {e}")
        else:
            log.error(f"Cannot remove {path}, unexpected error: {exc_info}")

    @classmethod
    def _log_locked_files(cls, path):
        """
        Log locked files if the platform allows.
        """
        system = sys.platform

        if system.startswith("win"):
            cls._log_locked_files_windows(path)
        elif system in ("linux", "darwin"):
            cls._log_locked_files_unix(path)
        else:
            log.warning(f"Unsupported platform '{system}'; cannot check locked files.")

    @staticmethod
    def _log_locked_files_windows(path):
        try:
            import psutil

            for proc in psutil.process_iter(["pid", "name"]):
                try:
                    for locked_file in proc.open_files():
                        if Path(locked_file.path) == path:
                            log.debug(
                                f"File locked by process {proc.info['name']} (PID: {proc.info['pid']})"
                            )
                except Exception:
                    continue
        except ImportError:
            log.warning("psutil is not installed; cannot log locked files on Windows.")
        except Exception as e:
            log.error(f"Failed to check locked files on Windows: {e}")

    @staticmethod
    def _log_locked_files_unix(path):
        try:
            proc_path = Path("/proc")

            if not proc_path.exists():
                log.warning(
                    "/proc filesystem is not available; cannot check locked files."
                )
                return

            for proc_dir in proc_path.iterdir():
                if not proc_dir.is_dir() or not proc_dir.name.isdigit():
                    continue

                fd_dir = proc_dir / "fd"
                if not fd_dir.exists():
                    continue

                for fd in fd_dir.iterdir():
                    try:
                        if fd.resolve() == path:
                            log.debug(
                                f"File locked by process {proc_dir.name} (FD: {fd.name})"
                            )
                    except Exception:
                        continue
        except Exception as e:
            log.error(f"Failed to check locked files on Unix-like system: {e}")

    @staticmethod
    def _calculate_backoff(attempt, base_delay):
        """
        Exponential backoff with jitter to reduce retry contention.
        """
        import random

        return base_delay * (2 ** (attempt - 1)) + random.uniform(0, 0.5)

    @staticmethod
    def get_relative_path(path):
        resolved_path = Path(path).resolve()
        try:
            relative_path = resolved_path.relative_to(Path.cwd())
            return str(relative_path)
        except ValueError:
            return str(resolved_path)

    @staticmethod
    def find_app_installation(
        exe_name, local_exe=None, winreg_path=None, winreg_key="", fallback_exe=None
    ):
        if not sys.platform.startswith("win"):
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
        if winreg_path and sys.platform.startswith("win"):
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
