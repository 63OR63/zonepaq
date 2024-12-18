# ![ZonePaq Toolkit](https://github.com/user-attachments/assets/9feab811-87b0-4c4a-bc54-379133e6b273)

## Description

**ZonePaq Toolkit** is an application designed for managing `.pak` **mods for S.T.A.L.K.E.R. 2**. The toolkit provides essential functionalities for **unpacking, repacking, and resolving conflicts** in mod files, ensuring smooth mod integration and reduced compatibility issues.

The application is user-friendly, featuring an intuitive GUI that allows modders to quickly identify and resolve conflicts. **ZonePaq Toolkit** comprises two main modules:

1. **Repacker** - Unpack `.pak` files and repack folders back into `.pak` archives.
2. **Conflict Resolver** - Analyze multiple `.pak` files for conflicts and assist in resolving overlapping files.

**ZonePaq Toolkit** ships with English and Russian translation of user interface and several color themes to choose from.

## Quick start

1. Download and install **[repak_cli](https://github.com/trumank/repak/releases)**
2. Download and install **[KDiff3](https://sourceforge.net/projects/kdiff3/files)** and/or **[WinMerge](https://winmerge.org/downloads)**
3. Download the latest release of **[ZonePaq Toolkit](https://github.com/63OR63/zonepaq/releases)**
4. Run `.exe` file and follow on-screen hints.

## Running from Source

### Requirements

- **Python 3.8+** (ensure it is installed on your system)
- **Python dependencies**: None. The application is built on default modules.
- **[repak_cli](https://github.com/trumank/repak)**, **[KDiff3](https://kdiff3.sourceforge.net)** and/or **[WinMerge](https://winmerge.org)**

### Steps to Install

1. Clone the repository to your local machine:

    ```bash
    git clone https://github.com/63OR63/zonepaq.git
    ```

2. Run `run.cmd` (if you're on Windows), `run.sh` (if you're on Linux) or execute in terminal:

    ```bash
    python zonepaq
    ```

## Compiling

You can compile an executable for your operating system by running `python build.py`

## Usage

1. **Open ZonePaq Toolkit** and go to the **Settings** menu.

2. Make sure the paths are set correctly. At a minimum, you need to set paths for:
    - **repak_cli**
    - Either **KDiff3** or **WinMerge**

3. Once your settings are configured, click **Save** and follow the on-screen instructions.

**Note:** It’s highly recommended to unpack the vanilla game files for better merging experience. Unpacking `pakchunk0-Windows.pak` should be sufficient. Game file are encrypted, so **AES decryption key** is included for this purpose. If the key changes in the future, you can retrieve the working one using [AESDumpster](https://github.com/GHFear/AESDumpster) and update it in **ZonePaq Toolkit** settings.

## Troubleshooting

- If you encounter any errors after changing settings, you can reset them to default by deleting the `settings.ini` file located in the same folder as the app.
- If you get some bug, please include latest logs from `logs/zonepaq.log` file in your report.

## FAQ

- ### What are `.pak` files in S.T.A.L.K.E.R. 2?

`.pak` files are archives that contain game assets, mods, or configuration files used in **S.T.A.L.K.E.R. 2** and other Unreal Engine games.

- ### Where are `.pak` files located?

The default location for **S.T.A.L.K.E.R. 2** is `%GAME_FOLDER%\Stalker2\Content\Paks`.

- ### What is the order `.pak` mods are loaded?

The order in which `.pak` files are loaded depends on their names. Files that come later alphabetically have higher priority. For example, `zzz_mod.pak` will override `z_mod.pak`.

If `zzz_mod.pak` contains `file1.cfg` and `z_mod.pak` contains both `file1.cfg` and `file2.cfg`, then only `file1.cfg` will be replaced, while `file2.cfg` will remain unchanged.

Additionally, if you add `_P` at the end of a `.pak` file's name, it will have even higher priority and override files in mods without this special suffix.

- ### Should I keep original mods after creating a merged one?

Typically, you copy the merged mod and delete the original mods it was merged from. However, mods often contain multiple files — some conflicting and others not. If you're unsure what you're doing, a more dirty yet robust approach is to rename the merged mod to something like `zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz_merged_P.pak` so it loads last and overwrites any conflicts, and can keep all the original mods in place.

- ### How does the merging in **ZonePaq Toolkit** works?

**ZonePaq Toolkit** uses a combination of **[repak_cli](https://github.com/trumank/repak)** and file comparison tools to compare files from multiple `.pak` archives. It highlights conflicting files and allows you to merge them into a single merged mod.

- ### Can I repack my mods after editing?

Yes! The **ZonePaq Toolkit** module will automatically repack files into a `.pak` archive after merging. Also, you can manually repack any folders.

- ### What external tools are supported for merging conflicts?

Currently, **[WinMerge](https://winmerge.org)** and **[KDiff3](https://kdiff3.sourceforge.net)** are supported.

- ### Can this Toolkit be used for other Unreal Engine games?

Theoretically, yes, but that wasn't tested by me. You can try and leave your feedback.

- ### Is the ZonePaq Toolkit free?

Yes, this tool is completely free and open source under the MIT License.
