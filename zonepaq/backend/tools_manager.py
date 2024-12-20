from pathlib import Path
from backend.logger import log
import requests
import shutil
import subprocess
import re

from backend.tools import Files
from config.settings import settings, translate


class ToolsManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.tools_base = settings.TOOLS["tools_base"]
        self.tools_base.mkdir(parents=True, exist_ok=True)

        self.seven_zip_local_path = (
            self.tools_base / "7z" / f'{settings.TOOLS["7zr"]["exe"]}.exe'
        )

        self.kdiff_installer = self.tools_base / "kdiff3_installer.exe"
        self.kdiff_extract_parameter = "bin"
        self.kdiff_output_dir = self.tools_base / "KDiff3"

    def download_file(self, url, target_file):
        try:
            Path(target_file).parent.mkdir(parents=True, exist_ok=True)
            log.info(f"Downloading {url}...")
            with requests.get(url, stream=True) as response:
                response.raise_for_status()
                with open(target_file, "wb") as f:
                    shutil.copyfileobj(response.raw, f, length=1024 * 1024)
            log.debug(f"Downloaded to {target_file}")
            return True
        except requests.RequestException as e:
            log.error(f"Download failed: {e}")
            return False

    def confirm_and_prepare_file(self, path, prompt_callback, prompt_name):
        """Confirm redownload and prepare file."""
        if path.exists() and not prompt_callback(prompt_name):
            log.info(f"Skipping {prompt_name}.")
            return False
        Files.delete_path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return True

    @staticmethod
    def get_latest_kdiff3(base_url=settings.TOOLS["kdiff3"]["base_url"]):
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

    def check_and_download_installer(
        self, url, target_file, tool_name, prompt_callback
    ):
        if not self.confirm_and_prepare_file(
            target_file,
            prompt_callback,
            f'{tool_name} {translate("dialogue_tools_redowndload_installer")}',
        ):
            log.info(f"Using existing {tool_name} installer.")
            return True
        return self.download_file(url, target_file)

    def extract_installer(self, installer_path, output_dir, extract_parameter="bin"):
        if not Files.is_existing_file(self.seven_zip_local_path):
            log.debug(f"Downloading 7z...")
            if not self.download_file(
                settings.TOOLS["7zr"]["direct_link"], self.seven_zip_local_path
            ):
                log.error(f"7z failed to download, aborting.")
                return False
        try:
            log.debug(f"Extracting installer: {installer_path}...")
            subprocess.run(
                [
                    str(self.seven_zip_local_path),
                    "x",
                    str(installer_path),
                    f"-ir!{extract_parameter}/*",
                    "-aoa",
                    f"-o{output_dir}",
                ],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            log.debug(f"Extraction of {installer_path} complete.")
            # Files.delete_path(installer_path)
            return True
        except subprocess.CalledProcessError as e:
            log.error(f"Extraction failed: {e}\nSTDOUT: {e.stdout}\nSTDERR: {e.stderr}")
        return False

    def download_and_extract_tool(
        self,
        url,
        installer_path,
        output_dir,
        tool_name,
        prompt_callback,
        extract_parameter="bin",
    ):
        if Files.is_existing_folder(output_dir):
            if not prompt_callback(
                f'{tool_name} {translate("dialogue_tools_reinstall")}'
            ):
                log.info(
                    f"{tool_name} already exists. Skipping download and installation."
                )
                return
            Files.delete_path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if self.check_and_download_installer(
            url, installer_path, tool_name, prompt_callback
        ) and self.extract_installer(installer_path, output_dir, extract_parameter):
            log.info(f"{tool_name} installation complete.")


if __name__ == "__main__":
    import tkinter as tk
    from tkinter import messagebox

    def prompt_redownload(item_name):
        root = tk.Tk()
        root.withdraw()
        result = messagebox.askyesno(
            "Redownload Confirmation", f"{item_name} exists. Redownload?"
        )
        root.destroy()
        return result

    tools_manager = ToolsManager()

    # KDiff3 Example
    if kdiff_url := tools_manager.get_latest_kdiff3():
        tools_manager.download_and_extract_tool(
            url=kdiff_url,
            installer_path=tools_manager.kdiff_installer,
            output_dir=tools_manager.kdiff_output_dir,
            tool_name="KDiff3",
            prompt_callback=prompt_redownload,
            extract_parameter="bin",
        )
    else:
        log.error("Failed to retrieve KDiff3 download URL.")
