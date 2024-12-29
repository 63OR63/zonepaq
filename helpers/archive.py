import os
import subprocess
import sys
from pathlib import Path

WORKING_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = WORKING_DIR / "archives"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if str(WORKING_DIR) not in sys.path:
    sys.path.insert(0, str(WORKING_DIR))

from zonepaq.config import metadata


def create_git_archive(app_name, app_version, archive_format="zip"):
    try:
        # Ensure the parent folder exists
        if not WORKING_DIR.exists():
            raise Exception(f"Parent folder does not exist: {WORKING_DIR}")

        # Change the working directory to the parent folder
        current_dir = Path.cwd()
        try:
            # Temporarily change the working directory
            os.chdir(WORKING_DIR)

            # Check if the directory is a Git repository
            if not (WORKING_DIR / ".git").exists():
                raise Exception("The specified folder is not a Git repository.")

            # Construct the archive name
            archive_name = f"{app_name} v{app_version} Source Code".replace(" ", "_")
            output_filename = OUTPUT_DIR / f"{archive_name}.{archive_format}"

            # Construct the git archive command
            command = [
                "git",
                "archive",
                f"--format={archive_format}",
                f"-o{output_filename}",
                "HEAD",
            ]

            # Execute the command
            subprocess.run(command, check=True)

            print(f"Archive created successfully: {output_filename}")
        finally:
            # Restore the original working directory
            os.chdir(current_dir)
    except subprocess.CalledProcessError as e:
        print(f"Error during git archive creation: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    archive_format = "zip"
    create_git_archive(
        metadata.APP_NAME, metadata.APP_VERSION, archive_format=archive_format
    )
