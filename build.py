import subprocess
import sys
from pathlib import Path

from PyInstaller.__main__ import run
from zonepaq.config import metadata

entry_point = r"zonepaq\__main__.py"
exe_name = f"{metadata.APP_NAME} v{metadata.APP_VERSION}".replace(" ", "_")


def create_version_file():

    version_file_content = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x4,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{metadata.APP_AUTHOR}'),
        StringStruct(u'FileDescription', u'{metadata.APP_DESCRIPTION_EN}'),
        StringStruct(u'FileVersion', u'{metadata.APP_VERSION}'),
        StringStruct(u'InternalName', u'zonepaq'),
        StringStruct(u'LegalCopyright', u'{metadata.COPYRIGHT}'),
        StringStruct(u'OriginalFilename', u'{exe_name}'),
        StringStruct(u'ProductName', u'{metadata.APP_NAME}'),
        StringStruct(u'ProductVersion', u'{metadata.APP_VERSION}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

    version_file_name = "version.rc"
    with open(version_file_name, "w", encoding="utf-8") as f:
        f.write(version_file_content)

    print(f"Spec file generated: {version_file_name}")
    return version_file_name


def build_win():
    version_file = create_version_file()

    args = [
        "--onefile",
        "--noconsole",
        "--name",
        exe_name,
        "--icon",
        metadata.APP_ICONS["ico"],
        "--version-file",
        version_file,
        "--additional-hooks-dir=hooks",
        entry_point,
    ]

    for file_type, file_path in metadata.APP_ICONS.items():
        args.extend(["--add-data", f"{file_path};{Path(file_path).parent}"])

    run(args)


def build_macos():
    args = [
        "--onefile",
        "--noconsole",
        "--name",
        exe_name,
        "--icon",
        metadata.APP_ICONS["icns"],
        "--add-data",
        f"{metadata.APP_ICONS['png']};{Path(metadata.APP_ICONS['png']).parent}",
        "--additional-hooks-dir=hooks",
        entry_point,
    ]

    run(args)


def build_linux():
    args = [
        "--onefile",
        "--noconsole",
        "--name",
        exe_name,
        "--icon",
        metadata.APP_ICONS["png"],
        "--add-data",
        f"{metadata.APP_ICONS['png']};{Path(metadata.APP_ICONS['png']).parent}",
        "--additional-hooks-dir=hooks",
        entry_point,
    ]

    run(args)


def install_requirements():
    try:
        print("Installing required packages from requirements.txt...")
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--upgrade",
                "-r",
                "requirements.txt",
            ]
        )
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while installing requirements: {e}")
        sys.exit(1)


def main():
    # install_requirements()

    if sys.platform.startswith("win"):
        build_win()
    elif sys.platform == "darwin":
        build_macos()
    elif sys.platform == "linux" or sys.platform == "linux2":
        build_linux()
    else:
        print("Unsupported platform: ", sys.platform)


if __name__ == "__main__":
    main()
