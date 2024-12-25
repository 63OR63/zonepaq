import logging
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from concurrent.futures import as_completed
from pathlib import Path

import requests
from backend.logger import log
from backend.repak import Repak
from backend.utilities import Data, Files
from config.settings_manager import settings
from config.translations import translate
from gui.window_messagebox import WindowMessageBox

# Suppress DEBUG logs from urllib3.connectionpool
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)


class ToolsManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls.init()
        return cls._instance

    @classmethod
    def init(cls):
        cls.tools_base = Path(settings.TOOLS["tools_base"])
        Files.create_dir(cls.tools_base)

        cls.seven_zip_local_exe = settings.TOOLS["7zr"]["local_exe"]

    @classmethod
    def install_repak_cli(
        cls, parent, install_metadata={"settings_key": "repak_cli"}, auto_mode=False
    ):
        install_metadata.update(settings.TOOLS["repak_cli"])
        return cls._install_tool(
            parent,
            download_method=cls.get_latest_github_release_asset,
            download_args={
                "github_repo": settings.TOOLS["repak_cli"]["github_repo"],
                "asset_regex": settings.TOOLS["repak_cli"]["asset_regex"],
            },
            install_metadata=install_metadata,
            auto_mode=auto_mode,
        )

    @classmethod
    def install_kdiff3(
        cls, parent, install_metadata={"settings_key": "kdiff3"}, auto_mode=False
    ):
        install_metadata.update(settings.TOOLS["kdiff3"])
        return cls._install_tool(
            parent,
            download_method=cls.get_latest_kdiff3,
            download_args={"base_url": settings.TOOLS["kdiff3"]["base_url"]},
            install_metadata=install_metadata,
            auto_mode=auto_mode,
        )

    @classmethod
    def install_winmerge(
        cls, parent, install_metadata={"settings_key": "winmerge"}, auto_mode=False
    ):
        install_metadata.update(settings.TOOLS["winmerge"])
        return cls._install_tool(
            parent,
            download_method=cls.get_latest_github_release_asset,
            download_args={
                "github_repo": settings.TOOLS["winmerge"]["github_repo"],
                "asset_regex": settings.TOOLS["winmerge"]["asset_regex"],
            },
            install_metadata=install_metadata,
            auto_mode=auto_mode,
        )

    @classmethod
    def unpack_file_by_index(
        cls,
        parent,
        install_metadata={},
        auto_mode=False,
        skip_aes_dumpster_download=False,
        skip_aes_extraction=False,
    ):
        if not skip_aes_extraction:
            cls.get_aes_key(
                parent=parent,
                auto_mode=True,
                skip_aes_dumpster_download=skip_aes_dumpster_download,
            )

        from backend.games_manager import GamesManager

        games_manager = GamesManager()

        results_ok = []
        results_ko = []
        futures = {}

        # Get the index from install_metadata
        file_index = install_metadata.get("index")
        if file_index is None or not (
            0 <= file_index < len(games_manager.vanilla_files)
        ):
            raise ValueError("Invalid or missing index in install_metadata")

        # Select the file based on the provided index
        item = games_manager.vanilla_files[file_index]
        vanilla_file = item["archive"]
        unpacked_folder = item["unpacked"]
        parent_folder = unpacked_folder.parent

        # Skip unpacking if unpacked_folder isn't empty
        if not Files.is_folder_empty(unpacked_folder):
            results_ok.append(
                f'{translate("generic_skipped")} {str(unpacked_folder)} {translate("generic_is_not_empty")}'
            )
        elif Files.is_existing_file(vanilla_file):
            vanilla_file = Path(vanilla_file)
            futures[
                Repak.unpack(
                    vanilla_file,
                    parent_folder,
                    allowed_extensions=[".cfg", ".ini"],
                )
            ] = vanilla_file

        for future in as_completed(futures):
            vanilla_file = futures[future]
            try:
                success, result = future.result()
                if success:
                    results_ok.append(str(vanilla_file))
                else:
                    results_ko.append(f"{str(vanilla_file)}: {result}")
            except Exception as e:
                results_ko.append(f"{str(vanilla_file)}: {str(e)}")

        if not auto_mode:
            cls.show_results(parent, results_ok, results_ko)

        return bool(results_ok) and not bool(results_ko)

    @staticmethod
    def show_results(parent, results_ok, results_ko):
        message_ok = "\n".join(results_ok) if results_ok else ""
        message_ko = "\n".join(results_ko) if results_ko else ""

        message = []
        if message_ok:
            message += [translate("generic_success") + ":", message_ok]
        if message_ko:
            message += [translate("generic_fail") + ":", message_ko]

        if message:
            WindowMessageBox.showinfo(parent, message=message)

    @classmethod
    def get_aes_key(
        cls,
        parent,
        install_metadata={"settings_key": "aes_key"},
        auto_mode=False,
        skip_aes_dumpster_download=False,
    ):
        try:
            if not skip_aes_dumpster_download:
                cls.install_aes_dumpster(parent=parent, auto_mode=True)

            from backend.games_manager import GamesManager

            games_manager = GamesManager()

            with tempfile.TemporaryDirectory() as temp_shipping_exe_dir:

                temp_shipping_exe_dir = Path(temp_shipping_exe_dir)
                temp_shipping_exe = temp_shipping_exe_dir / "shipping.exe"
                Files.copy_path(
                    games_manager.shipping_exe,
                    temp_shipping_exe,
                )
                aes_dumpster_exe = settings.TOOLS_PATHS["aes_dumpster"]

                command = [str(aes_dumpster_exe), str(temp_shipping_exe)]

                process = subprocess.Popen(
                    command,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                )
                process.stdin.write(b"\n")  # Sending a newline to end AESDumpster
                process.stdin.flush()

                stdout, stderr = process.communicate()
                aes_output = stdout.decode("utf-8")

                # Extract the AES key using a regex
                key_pattern = r"0x[0-9A-F]{64}"
                match = re.search(key_pattern, aes_output)

                if not match:
                    if not auto_mode:
                        message = f'{translate("dialogue_get_aes_error")}\n{translate("dialogue_check_logs")}'
                        WindowMessageBox.showinfo(parent, message=message)
                    return False

                aes_key = str(match.group(0))

                if Data.is_valid_aes_key(aes_key):
                    # Finalize
                    settings_key = install_metadata.get("settings_key", None)
                    entry_widget = install_metadata.get("entry_widget", None)
                    entry_variable = install_metadata.get("entry_variable", None)

                    if settings_key:
                        settings.update_config("SETTINGS", "aes_key", aes_key)

                    if entry_variable and entry_widget:
                        entry_variable.set(aes_key)
                        parent._apply_style(True, entry_widget)

                    if not auto_mode:
                        message = translate("dialogue_get_aes_success")
                        WindowMessageBox.showinfo(parent, message=message)
                    return True
                else:
                    if not auto_mode:
                        message = f'{translate("dialogue_get_aes_error")}\n{translate("dialogue_check_logs")}'
                        WindowMessageBox.showinfo(parent, message=message)
                    return False

        except Exception as e:
            if not auto_mode:
                message = [f'{translate("dialogue_get_aes_error")}\nError:', str(e)]
                WindowMessageBox.showinfo(parent, message=message)
            return False

    @classmethod
    def install_aes_dumpster(
        cls, parent, install_metadata={"settings_key": "aes_dumpster"}, auto_mode=False
    ):
        install_metadata.update(settings.TOOLS["aes_dumpster"])
        return cls._install_tool(
            parent,
            download_method=cls.get_latest_github_release_asset,
            download_args={
                "github_repo": settings.TOOLS["aes_dumpster"]["github_repo"],
                "asset_regex": settings.TOOLS["aes_dumpster"]["asset_regex"],
            },
            install_metadata=install_metadata,
            skip_extract=True,
            auto_mode=auto_mode,
        )

    @classmethod
    def _install_tool(
        cls,
        parent,
        download_method,
        download_args,
        install_metadata,
        skip_extract=False,
        auto_mode=False,
        check_platform=True,
        skip_search=False,
    ):
        # Check platform compatibility
        if check_platform and not sys.platform.startswith("win"):
            if not auto_mode:
                WindowMessageBox.showerror(
                    parent,
                    message=translate("dialogue_only_windows"),
                )
            return False

        # Extract variables from metadata dict
        settings_key = install_metadata.get("settings_key", None)
        display_name = install_metadata.get("display_name", None)
        exe_name = install_metadata.get("exe_name", None)
        local_exe = install_metadata.get("local_exe", None)
        fallback_exe = install_metadata.get("fallback_exe", None)
        extract_parameter = install_metadata.get("extract_parameter", None)
        winreg_path = install_metadata.get("winreg_path", None)
        winreg_key = install_metadata.get("winreg_key", None)
        entry_widget = install_metadata.get("entry_widget", None)
        entry_variable = install_metadata.get("entry_variable", None)

        # Try to find existing installation
        found_exe = None
        if not skip_search:
            try:
                suggested_path = Files.find_app_installation(
                    exe_name, local_exe, winreg_path, winreg_key, fallback_exe
                )
                if Files.is_existing_file(suggested_path):
                    found_exe = suggested_path
            except:
                pass

        if found_exe:
            log.info(f"Skipping {display_name} download and installation.")
            exe_location = found_exe

        else:
            # Download the tool
            download_url = download_method(**download_args)
            if not download_url:
                if not auto_mode:
                    WindowMessageBox.showerror(
                        parent,
                        message=f'{translate("dialogue_install_error")} {display_name}\n{translate("dialogue_check_logs")}',
                    )
                return False

            # Download and extract the tool
            install_result = cls.download_and_extract_tool(
                parent,
                url=download_url,
                local_exe=local_exe,
                display_name=display_name,
                skip_extract=skip_extract,
                extract_parameter=extract_parameter,
                auto_mode=auto_mode,
            )

            if not install_result:
                if not auto_mode:
                    WindowMessageBox.showerror(
                        parent,
                        message=f'{translate("dialogue_install_error")} {display_name}\n{translate("dialogue_check_logs")}',
                    )
                return False

            # Validate download
            if Files.is_existing_file(local_exe):
                exe_location = local_exe
            else:
                log.error(f"{display_name} can't be located at {local_exe}")
                if not auto_mode:
                    WindowMessageBox.showerror(
                        parent,
                        message=f'{translate("dialogue_install_error")} {display_name}\n{translate("dialogue_check_logs")}',
                    )
                return False

        # Finalize installation
        if settings_key:
            path = Files.get_relative_path(exe_location)
            # settings.TOOLS_PATHS[settings_key] = str(path)
            # settings.save()
            settings.update_config("TOOLS_PATHS", settings_key, str(path))

        if entry_variable and entry_widget:
            entry_variable.set(path)
            parent._apply_style(True, entry_widget)

        if not auto_mode:
            if found_exe:
                message = translate("dialogue_install_found")
            else:
                message = translate("dialogue_install_success")

            WindowMessageBox.showinfo(
                parent,
                message=f"{display_name} {message} {exe_location}",
            )

        return True

    @classmethod
    def download_and_extract_tool(
        cls,
        parent,
        url,
        local_exe,
        display_name,
        skip_extract,
        extract_parameter,
        auto_mode=False,
    ):

        output_dir = Path(local_exe).parent
        file_extension = re.search(r"\.([a-zA-Z0-9]+)(?:\?|#|$)", url).group(1)
        if file_extension == "exe":
            installer_suffix = "Installer"
        else:
            installer_suffix = "Archive"
        installer_path = (
            cls.tools_base / f"{display_name} {installer_suffix}.{file_extension}"
        )

        # Detele the output directory is not empty
        if not Files.is_folder_empty(output_dir):
            Files.delete_path(output_dir)

        # Ensure the output directory exists
        Files.create_dir(output_dir)

        # Download installer
        log.info(f"Downloading {display_name}...")
        downloaded_file = cls.check_and_download_installer(
            parent, url, installer_path, display_name, auto_mode
        )

        if not downloaded_file:
            return False

        # Skip extraction if it's a direct executable
        if skip_extract:
            log.debug(f"Skipping extraction of {display_name}.")
            Files.move_path(installer_path, local_exe)
            log.info(f"{display_name} installation complete.")
            return True

        # Extract installer
        log.info(f"Extracting {display_name}...")
        extraction_success = cls.extract_installer(
            installer_path, output_dir, extract_parameter
        )

        if not extraction_success:
            return False

        log.info(f"{display_name} installation complete.")
        return True

    @staticmethod
    def get_latest_kdiff3(base_url, timeout=10):
        try:
            log.debug(f"Querying {base_url}...")
            # Use a context manager for the HTTP request
            with requests.get(base_url, timeout=timeout) as response:
                response.raise_for_status()  # Raise an error for HTTP status codes

                # Parse the response text for matches
                matches = re.findall(
                    r'href="(kdiff3-\d+(\.\d+)*-windows-(x86_64|64)\.exe)"',
                    response.text,
                )

                if not matches:
                    log.error(
                        "No valid KDiff3 URLs found. The download page may have changed."
                    )
                    return None

                # Sort and identify the latest version
                latest = max(
                    matches, key=lambda x: list(map(int, re.findall(r"\d+", x[0])))
                )[0]

                latest_url = f"{base_url}{latest}"
                log.debug(f"Latest KDiff3 URL: {latest_url}")
                return latest_url

        except requests.Timeout:
            log.exception(f"Request to {base_url} timed out after {timeout} seconds.")
        except requests.RequestException as e:
            log.exception(f"Error fetching KDiff3 URL: {e}")
        except ValueError as e:
            log.exception(f"Error parsing version information: {e}")

        return None

    @staticmethod
    def get_latest_github_release_asset(github_repo, asset_regex):
        try:
            log.debug(f"Querying {github_repo} Github repo...")
            response = requests.get(
                f"https://api.github.com/repos/{github_repo}/releases/latest"
            )
            response.raise_for_status()
            release_data = response.json()

            for asset in release_data.get("assets", []):
                asset_name = asset.get("name", "")
                if re.search(asset_regex, asset_name):
                    download_url = asset.get("browser_download_url")
                    log.debug(f"Latest {github_repo} asset URL: {download_url}")
                    return download_url

            log.error(f"No matching asset found for {github_repo}.")
            return None

        except requests.exceptions.RequestException as e:
            log.exception(f"Error fetching release data: {e}")
            return None

    @classmethod
    def check_and_download_installer(
        cls, parent, url, target_file, display_name, auto_mode
    ):
        # Check if the installer needs to be confirmed and prepared
        if target_file.exists():
            if auto_mode:
                user_confirmation = False
            else:
                user_confirmation = WindowMessageBox.askyesno(
                    parent,
                    message=f'{display_name} {translate("dialogue_tools_redowndload_installer")}',
                )

            if not user_confirmation:
                log.info(f"Using existing {display_name} installer.")
                return True

        # Prepare the target file directory
        Files.create_dir(target_file.parent)
        Files.delete_path(target_file)

        # Download the file
        downloaded_file = cls.download_file(url, target_file)

        return downloaded_file

    # @classmethod
    # def download_file(cls, url, target_file):
    #     try:
    #         target_file = Path(target_file)
    #         Files.create_dir(target_file.parent)
    #         log.debug(f"Downloading {url}...")
    #         with requests.get(url, stream=True) as response:
    #             response.raise_for_status()
    #             with open(target_file, "wb") as f:
    #                 shutil.copyfileobj(response.raw, f, length=1024 * 1024)
    #         log.debug(f"Downloaded to {str(target_file)}")
    #         return True
    #     except requests.RequestException as e:
    #         log.exception(f"Download failed: {e}")
    #         return False

    @classmethod
    def download_file(cls, url, target_file, timeout=30):
        try:
            target_file = Path(target_file)
            Files.create_dir(target_file.parent)

            log.debug(f"Starting download: {url}")

            with requests.get(url, stream=True, timeout=timeout) as response:
                response.raise_for_status()
                content_type = response.headers.get("Content-Type", "")
                if not content_type.startswith("application/octet-stream"):
                    log.warning(f"Unexpected content type: {content_type}")
                    return False

                temp_file = target_file.with_suffix(".tmp")
                with open(temp_file, "wb") as f:
                    shutil.copyfileobj(response.raw, f, length=1024 * 1024)
                temp_file.rename(target_file)

            log.debug(f"Successfully downloaded to {target_file}")
            return True
        except requests.Timeout:
            log.error(f"Download timed out: {url}")
        except requests.RequestException as e:
            log.exception(f"Download failed: {e}")
        except Exception as e:
            log.exception(f"Unexpected error: {e}")
        return False

    @classmethod
    def extract_installer(cls, installer_path, output_dir, extract_parameter=""):
        file_extension = installer_path.suffix[1:] if installer_path.suffix else None

        if file_extension in {"7z", "exe"}:
            return cls._extract_with_7zr(installer_path, output_dir, extract_parameter)

        elif file_extension == "zip":
            return cls._extract_with_zipfile(
                installer_path, output_dir, extract_parameter
            )

        else:
            log.error(f"Unsupported archive format: {file_extension}")
            return False

    @classmethod
    def _extract_with_7zr(cls, installer_path, output_dir, extract_parameter=None):
        if not Files.is_existing_file(cls.seven_zip_local_exe):
            log.debug("Downloading 7z...")
            if not cls.download_file(
                settings.TOOLS["7zr"]["direct_link"], cls.seven_zip_local_exe
            ):
                log.error("7z failed to download, aborting.")
                return False

        try:
            log.debug(f"Extracting installer with 7zr: {installer_path}...")
            with tempfile.TemporaryDirectory() as temp_unpack_dir:
                temp_unpack_dir = Path(temp_unpack_dir)
                command = [
                    str(cls.seven_zip_local_exe),
                    "x",
                    str(installer_path),
                    "-aoa",
                    f"-o{temp_unpack_dir}",
                ]
                if extract_parameter:
                    command.insert(3, extract_parameter)

                # Extract
                subprocess.run(
                    command,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                # Copy all from temp_unpack_dir to output_dir
                source_dir = temp_unpack_dir
                if extract_parameter:
                    source_dir /= extract_parameter
                Files.copy_folder_contents(source_dir, output_dir)

            log.debug(f"Extraction of {installer_path} complete.")
            return True
        except subprocess.CalledProcessError as e:
            log.exception(
                f"Extraction failed: {e}\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}"
            )
            return False

    @classmethod
    def _extract_with_zipfile(cls, installer_path, output_dir, extract_parameter=None):
        if not zipfile.is_zipfile(installer_path):
            log.error(f"{installer_path} is not a valid ZIP file.")
            return False

        try:
            log.debug(f"Extracting installer with ZIP: {installer_path}...")
            with tempfile.TemporaryDirectory() as temp_unpack_dir:
                temp_unpack_dir = Path(temp_unpack_dir)

                # Extract
                with zipfile.ZipFile(installer_path, "r") as zip_ref:
                    files_to_extract = (
                        [
                            f
                            for f in zip_ref.namelist()
                            if f.startswith(f"{extract_parameter}/")
                        ]
                        if extract_parameter
                        else zip_ref.namelist()
                    )

                    if not files_to_extract:
                        log.error(
                            f"No files found matching parameter: {extract_parameter}/"
                        )
                        return False

                    zip_ref.extractall(temp_unpack_dir, members=files_to_extract)

                # Copy all from temp_unpack_dir to output_dir
                source_dir = temp_unpack_dir
                if extract_parameter:
                    source_dir /= extract_parameter
                Files.copy_folder_contents(source_dir, output_dir)

            log.debug(f"Extraction of {installer_path} complete.")
            return True
        except Exception as e:
            log.exception(f"Extraction failed: {e}")
            return False
