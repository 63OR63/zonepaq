from pathlib import Path
import tempfile
from backend.logger import log
import requests
import shutil
import subprocess
import re
import zipfile

from backend.tools import Files
from config.settings import settings, translate
from urllib.parse import urlparse


class ToolsManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.auto_mode = False
        self.prompt_callback = None

        self.tools_base = Path(settings.TOOLS["tools_base"])
        self.tools_base.mkdir(parents=True, exist_ok=True)

        self.seven_zip_local_exe = settings.TOOLS["7zr"]["local_exe"]

    def download_file(self, url, target_file):
        try:
            target_file = Path(target_file)
            target_file.parent.mkdir(parents=True, exist_ok=True)
            log.info(f"Downloading {url}...")
            with requests.get(url, stream=True) as response:
                response.raise_for_status()
                with open(target_file, "wb") as f:
                    shutil.copyfileobj(response.raw, f, length=1024 * 1024)
            log.debug(f"Downloaded to {str(target_file)}")
            return True
        except requests.RequestException as e:
            log.exception(f"Download failed: {e}")
            return False

    @staticmethod
    def get_latest_kdiff3(base_url, timeout=10):
        try:
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
                log.info(f"Latest KDiff3 URL: {latest_url}")
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
            response = requests.get(
                f"https://api.github.com/repos/{github_repo}/releases/latest"
            )
            response.raise_for_status()
            release_data = response.json()

            for asset in release_data.get("assets", []):
                asset_name = asset.get("name", "")
                if re.search(asset_regex, asset_name):
                    return asset.get("browser_download_url")

            log.error(f"No matching asset found for {github_repo}.")
            return None

        except requests.exceptions.RequestException as e:
            log.exception(f"Error fetching release data: {e}")
            return None

    def check_and_download_installer(self, url, target_file, display_name):
        # Check if the installer needs to be confirmed and prepared
        if target_file.exists():
            user_confirmation = self.prompt_callback(
                f'{display_name} {translate("dialogue_tools_redowndload_installer")}',
                auto_mode=self.auto_mode,
            )

            if not user_confirmation:
                log.info(f"Using existing {display_name} installer.")
                return True

        # Prepare the target file directory
        Files.delete_path(target_file)
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # Download the file
        downloaded_file = self.download_file(url, target_file)

        return downloaded_file

    def extract_installer(self, installer_path, output_dir, extract_parameter=""):
        file_extension = installer_path.suffix[1:] if installer_path.suffix else None

        if file_extension in {"7z", "exe"}:
            return self._extract_with_7zr(installer_path, output_dir, extract_parameter)

        elif file_extension == "zip":
            return self._extract_with_zipfile(
                installer_path, output_dir, extract_parameter
            )

        else:
            log.error(f"Unsupported archive format: {file_extension}")
            return False

    def _extract_with_7zr(self, installer_path, output_dir, extract_parameter=None):
        if not Files.is_existing_file(self.seven_zip_local_exe):
            log.debug("Downloading 7z...")
            if not self.download_file(
                settings.TOOLS["7zr"]["direct_link"], self.seven_zip_local_exe
            ):
                log.error("7z failed to download, aborting.")
                return False

        try:
            log.debug(f"Extracting installer with 7zr: {installer_path}...")
            with tempfile.TemporaryDirectory() as temp_unpack_dir:
                temp_unpack_dir = Path(temp_unpack_dir)
                command = [
                    str(self.seven_zip_local_exe),
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
                Files.copy_folder_contents(temp_unpack_dir, output_dir)

            log.debug(f"Extraction of {installer_path} complete.")
            return True
        except subprocess.CalledProcessError as e:
            log.exception(
                f"Extraction failed: {e}\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}"
            )
            return False

    def _extract_with_zipfile(self, installer_path, output_dir, extract_parameter=None):
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
                Files.copy_folder_contents(temp_unpack_dir, output_dir)

            log.debug(f"Extraction of {installer_path} complete.")
            return True
        except Exception as e:
            log.exception(f"Extraction failed: {e}")
            return False

    def download_and_extract_tool(
        self,
        url,
        local_exe,
        display_name,
        prompt_callback,
        skip_extract,
        extract_parameter,
        auto_mode=False,
    ):
        self.auto_mode = auto_mode
        self.prompt_callback = prompt_callback

        output_dir = Path(local_exe).parent
        file_extension = re.search(r"\.([a-zA-Z0-9]+)(?:\?|#|$)", url).group(1)
        if file_extension == "exe":
            installer_suffix = "Installer"
        else:
            installer_suffix = "Archive"
        installer_path = (
            self.tools_base / f"{display_name} {installer_suffix}.{file_extension}"
        )

        # Detele the output directory is not empty
        if not Files.is_folder_empty(output_dir):
            Files.delete_path(output_dir)

        # Ensure the output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Download installer
        downloaded_file = self.check_and_download_installer(
            url, installer_path, display_name
        )

        if not downloaded_file:
            return False

        # Skip extraction if it's a direct executable
        if skip_extract:
            log.debug(f"Skipping extraction of {display_name}.")
            shutil.move(installer_path, local_exe)
            return True

        # Extract installer
        extraction_success = self.extract_installer(
            installer_path, output_dir, extract_parameter
        )

        if not extraction_success:
            return False

        log.info(f"{display_name} installation complete.")
        return True
