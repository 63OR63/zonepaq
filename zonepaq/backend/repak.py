import shutil
import subprocess
from pathlib import Path

from backend.executor import run_in_executor
from backend.logger import log
from backend.utilities import Files
from config.settings import settings


class Repak:
    """Provides methods for listing, unpacking, and repacking files using the Repak CLI tool."""

    REPAK_PATH = settings.TOOLS_PATHS["repak_cli"]

    @classmethod
    @run_in_executor
    def get_list(cls, file):
        log.debug(f"Attempting to list contents of the file: {file}")
        try:
            repak_path = cls.REPAK_PATH

            if not Files.is_existing_file_type(repak_path, ".exe"):
                raise FileNotFoundError(f"repak_cli doesn't exist at {repak_path}")

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
    def unpack(cls, source, destination, aes_key=None):
        log.debug(
            f'Attempting to unpack: {source}{" using key: " + aes_key if aes_key else ""}'
        )
        try:
            repak_path = cls.REPAK_PATH
            if not Files.is_existing_file_type(repak_path, ".exe"):
                raise FileNotFoundError(f"repak doesn't exist at {repak_path}")

            source = Path(source)
            destination = Path(destination)
            unpacked_folder = Path(source).with_suffix("")

            Files.delete_path(unpacked_folder)

            command = [repak_path]
            if aes_key:
                command.extend(["-a", aes_key])
            command.extend(["unpack", str(source)])

            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                if (
                    not aes_key
                    and "pak is encrypted but no key was provided"
                    in result.stderr.strip()
                ):
                    log.warning(f"{source} is encrypted, trying again with AES key")
                    future = cls.unpack(source, destination, settings.AES_KEY)
                    success, output = future.result()
                    return success, output

                log.error(f"Failed to unpack {source}: {result.stderr.strip()}")
                raise RuntimeError(
                    f"Command failed with error:\n{result.stderr.strip()}"
                )

            target_folder = destination / unpacked_folder.name

            if unpacked_folder != target_folder:
                Files.delete_path(target_folder)
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
            repak_path = cls.REPAK_PATH
            if not Files.is_existing_file_type(repak_path, ".exe"):
                raise FileNotFoundError(f"repak doesn't exist at {repak_path}")

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
