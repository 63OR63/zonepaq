from pathlib import Path
import subprocess

# Define the working directory
WORKING_DIR = Path(__file__).resolve().parent.parent


def run_pipreqs():
    # Run pipreqs to regenerate requirements.txt
    subprocess.run(["pipreqs", str(WORKING_DIR), "--force"])


def parse_and_update_requirements():
    # Path to the requirements.txt file
    requirements_path = WORKING_DIR / "requirements.txt"

    # Read the requirements.txt file
    with open(requirements_path, "r") as file:
        lines = file.readlines()

    # Dictionary to store the highest version for each package
    requirements = {}

    # Parse each line and process package names and versions
    for line in lines:
        line = line.strip()
        if "==" in line:
            package, version = line.split("==")
            if package not in requirements:
                requirements[package] = version
            else:
                # If the current version is greater, update the version
                if version > requirements[package]:
                    requirements[package] = version

    # Create the updated requirements.txt content with >=
    updated_lines = [
        f"{package}>={version}\n" for package, version in requirements.items()
    ]

    # Write the updated content back to requirements.txt
    with open(requirements_path, "w") as file:
        file.writelines(updated_lines)


if __name__ == "__main__":
    run_pipreqs()  # Run pipreqs to regenerate the requirements.txt
    parse_and_update_requirements()  # Parse and update the requirements.txt
