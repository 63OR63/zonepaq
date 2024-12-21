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


class ToolsManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.auto_mode = False
        self.prompt_callback = None

        self.tools_base = settings.TOOLS["tools_base"]
        self.tools_base.mkdir(parents=True, exist_ok=True)

        self.seven_zip_local_path = (
            self.tools_base / "7zr" / f'{settings.TOOLS["7zr"]["exe"]}.exe'
        )

        self.repak_asset_regex = r"repak_cli-x86_64-pc-windows-msvc.zip$"
        self.repak_installer = self.tools_base / "repak_archive.zip"
        self.repak_extract_method = "zipfile"
        self.repak_extract_parameter = ""
        self.repak_output_dir = self.tools_base / "repak_cli"
        self.repak_local_path = (
            self.repak_output_dir / f'{settings.TOOLS["repak_cli"]["exe"]}.exe'
        )

        self.kdiff3_installer = self.tools_base / "kdiff3_installer.exe"
        self.kdiff3_extract_method = "7zr"
        self.kdiff3_extract_parameter = "bin"
        self.kdiff3_output_dir = self.tools_base / "KDiff3"
        self.kdiff3_local_path = (
            self.kdiff3_output_dir / f'{settings.TOOLS["kdiff3"]["exe"]}.exe'
        )

        self.winmerge_asset_regex = r"winmerge-\d+(\.\d+)*-exe.zip$"
        self.winmerge_installer = self.tools_base / "winmerge_archive.zip"
        self.winmerge_extract_method = "zipfile"
        self.winmerge_extract_parameter = "WinMerge"
        self.winmerge_output_dir = self.tools_base / "WinMerge"
        self.winmerge_local_path = (
            self.winmerge_output_dir / f'{settings.TOOLS["winmerge"]["exe"]}.exe'
        )

        self.aes_dumpster_asset_regex = r"AESDumpster-Win64.exe$"
        self.aes_dumpster_extract_method = None
        self.aes_dumpster_output_dir = self.tools_base / "aes_dumpster"
        self.aes_dumpster_local_path = (
            self.aes_dumpster_output_dir
            / f'{settings.TOOLS["aes_dumpster"]["exe"]}.exe'
        )

    def download_file(self, url, target_file):
        try:
            log.info(f"Downloading {url}...")

            # Use a context manager to safely handle the response
            with requests.get(url, stream=True) as response:
                response.raise_for_status()  # Raise an error for HTTP errors

                # Open the target file and write the content in chunks
                with open(target_file, "wb") as f:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:  # Filter out keep-alive chunks
                            f.write(chunk)

            log.debug(f"Downloaded to {target_file}")
            return True

        except requests.RequestException as e:
            log.error(f"Download failed: {e}")
            return False

    @staticmethod
    def get_latest_kdiff3(base_url):
        try:
            response = requests.get(base_url)
            response.raise_for_status()
            matches = re.findall(
                r'href="(kdiff3-\d+(\.\d+)*-windows-(x86_64|64)\.exe)"', response.text
            )
            if not matches:
                log.error(
                    "No valid KDiff3 URLs found. Probably, the download page has changed."
                )
                return None
            if matches:
                latest = sorted(
                    matches,
                    key=lambda x: list(map(int, re.findall(r"\d+", x[0]))),
                    reverse=True,
                )[0][0]
                return f"{base_url}{latest}"
        except requests.RequestException as e:
            log.error(f"Error fetching KDiff3 URL: {e}")
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
            log.error(f"Error fetching release data: {e}")
            return None

    def check_and_download_installer(self, url, target_file, tool_name):
        # Check if the installer needs to be confirmed and prepared
        if target_file.exists():
            user_confirmation = self.prompt_callback(
                f'{tool_name} {translate("dialogue_tools_redowndload_installer")}',
                auto_mode=self.auto_mode,
            )

            if not user_confirmation:
                log.info(f"Using existing {tool_name} installer.")
                return True

        # Prepare the target file directory
        Files.delete_path(target_file)
        target_file.parent.mkdir(parents=True, exist_ok=True)

        # Download the file
        download_success = self.download_file(url, target_file)

        return download_success

    def extract_installer(
        self, installer_path, output_dir, extract_method="zipfile", extract_parameter=""
    ):
        if extract_method not in {"7zr", "zipfile"}:
            log.error(f"Unsupported extract method: {extract_method}")
            return False

        if extract_method == "7zr":
            return self._extract_with_7zr(installer_path, output_dir, extract_parameter)

        if extract_method == "zipfile":
            return self._extract_with_zipfile(
                installer_path, output_dir, extract_parameter
            )

    def _extract_with_7zr(self, installer_path, output_dir, extract_parameter):
        if not Files.is_existing_file(self.seven_zip_local_path):
            log.debug("Downloading 7z...")
            if not self.download_file(
                settings.TOOLS["7zr"]["direct_link"], self.seven_zip_local_path
            ):
                log.error("7z failed to download, aborting.")
                return False

        try:
            log.debug(f"Extracting installer with 7zr: {installer_path}...")
            with tempfile.TemporaryDirectory() as temp_unpack_dir:
                temp_unpack_dir = Path(temp_unpack_dir)
                command = [
                    str(self.seven_zip_local_path),
                    "x",
                    str(installer_path),
                    "-aoa",
                    f"-o{temp_unpack_dir}",
                ]
                if extract_parameter:
                    command.insert(3, extract_parameter)

                subprocess.run(
                    command,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                shutil.copytree(
                    temp_unpack_dir / extract_parameter, output_dir, dirs_exist_ok=True
                )
            log.debug(f"Extraction of {installer_path} complete.")
            return True
        except subprocess.CalledProcessError as e:
            log.error(f"Extraction failed: {e}\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")
            return False

    def _extract_with_zipfile(self, installer_path, output_dir, extract_parameter):
        if not zipfile.is_zipfile(installer_path):
            log.error(f"{installer_path} is not a valid ZIP file.")
            return False

        try:
            log.debug(f"Extracting installer with ZIP: {installer_path}...")
            with tempfile.TemporaryDirectory() as temp_unpack_dir:
                temp_unpack_dir = Path(temp_unpack_dir)
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
                shutil.copytree(
                    temp_unpack_dir / extract_parameter, output_dir, dirs_exist_ok=True
                )
            log.debug(f"Extraction of {installer_path} complete.")
            return True
        except Exception as e:
            log.error(f"Extraction failed: {e}")
            return False

    def download_and_extract_tool(
        self,
        url,
        installer_path,
        output_dir,
        tool_name,
        prompt_callback,
        extract_method,
        extract_parameter,
        auto_mode=False,
    ):
        self.auto_mode = auto_mode
        self.prompt_callback = prompt_callback

        # Check if output directory is not empty
        if not Files.is_folder_empty(output_dir):
            user_wants_reinstall = prompt_callback(
                f'{tool_name} {translate("dialogue_tools_reinstall")}',
                auto_mode=auto_mode,
            )

            if not user_wants_reinstall:
                log.info(
                    f"{tool_name} already exists. Skipping download and installation."
                )
                return False, True

            # User agreed to reinstall; delete existing directory
            Files.delete_path(output_dir)

        # Ensure the output directory exists
        output_dir.mkdir(parents=True, exist_ok=True)

        # Download installer
        download_success = self.check_and_download_installer(
            url, installer_path, tool_name
        )

        if not download_success:
            return False, False

        # Skip extraction if it's a direct executable
        if extract_method == None:
            log.info(f"{tool_name} executable downloaded successfully.")
            return True, False

        # Extract installer
        extraction_success = self.extract_installer(
            installer_path, output_dir, extract_method, extract_parameter
        )

        if not extraction_success:
            return False, False

        log.info(f"{tool_name} installation complete.")
        return True, False
