# ![ZonePaq Toolkit](https://github.com/user-attachments/assets/9feab811-87b0-4c4a-bc54-379133e6b273)

## Description

**ZonePaq Toolkit** is an application designed for managing `.pak` **mods for S.T.A.L.K.E.R. 2**. The toolkit provides essential functionalities for **unpacking, repacking, and resolving conflicts** in mod files, ensuring smooth mod integration and reduced compatibility issues.

The application is user-friendly, featuring an intuitive GUI that allows modders to quickly identify and resolve conflicts. **ZonePaq Toolkit** comprises two main modules:

1. **Repacker** - Unpack `.pak` files and repack folders back into `.pak` archives.
2. **Conflict Resolver** - Analyze multiple `.pak` files for conflicts and assist in resolving overlapping files.

**ZonePaq Toolkit** utilizes a combination of next external tools for operation:

- **[repak_cli](https://github.com/trumank/repak)** for unpacking and repacking `.pak` files.
- **[KDiff3](https://kdiff3.sourceforge.net)** or **[WinMerge](https://winmerge.org)** for comparing and merging unpacked mods.
- **[AESDumpster](https://github.com/GHFear/AESDumpster)** for getting AES encryption key, used to unpack vanilla files.
- **[7zr](https://7-zip.org)** for extracting Windows PE installers.

All required tools can be downloaded and installed automatically.

**ZonePaq Toolkit** ships with English and Russian translation of user interface and several color themes to choose from.

## Quick start

1. Download the **[latest release](https://github.com/63OR63/zonepaq/releases/latest)**
2. Run `.exe` file and follow on-screen hints.

**Note:** Running from source may offers superior performance in some conditions.

## Running from Source

1. Install **Python 3.8 or later**

2. Clone the repository to your local machine:

    ```cmd
    git clone https://github.com/63OR63/zonepaq && cd zonepaq
    ```

3. Install requirements:

    ```cmd
    pip install --upgrade -r requirements.txt
    ```

4. Run `run.cmd` or execute in terminal:

    ```cmd
    pythonw zonepaq
    ```

**Note:** You may want to check these issues in utilized libraries (fixes have been applied in the compiled version): [1](https://github.com/Akascape/CTkToolTip/issues/20), [2](https://github.com/TomSchimansky/CustomTkinter/pull/2162)

## Compiling

You can compile an executable for your operating system by running `python build.py`

**Note:** full functionality is guaranteed only on Windows.

## Usage

1. **Open ZonePaq Toolkit**. On first launch you will be prompted to install all needed tools.

2. Follow the hints that are built-in in GUI. You can disable them in the settings once you're acquianted with the workflow.

3. If you wish to change any settings, go to the **Settings** menu by clicking the **cog button** on main screens.

## Troubleshooting

- If you encounter any errors, first try resetting the settings to default by deleting the `zonepaq/settings.ini` file.
- If you get some bug, please open an issue on GitHub and include `logs/zonepaq.log` file contents in your report.

## FAQ

- ### What are `.pak` files in S.T.A.L.K.E.R. 2?

`.pak` files are archives that contain game assets, mods, or configuration files used in **S.T.A.L.K.E.R. 2** and some other **Unreal Engine** games.

- ### Where are `.pak` files located?

The default location for **S.T.A.L.K.E.R. 2** is `%GAME_FOLDER%\Stalker2\Content\Paks`.

- ### What is the order `.pak` mods are loaded?

`.pak` files are loaded in alphabetical order, with files later in the order having higher priority. When multiple files contain the same resource, the version from the higher-priority `.pak` file will override others. Adding `_P` to the end of a `.pak` file's name gives it the highest priority, overriding files in mods without the suffix. Additionally, if you prepend `_P` with a number, it will affect the priority as well, so `a_2_P.pak` will override `z_1_P.pak`, even though `a` comes before `z`.

- ### How to merge mods if there're too many mods changing the same file?

To resolve complex conflicts, create a merged mod for groups of 2 or 3 mods, then proceed to merge these intermediate merged mods together.

- ### Should I keep original mods after creating a merged one?

Generally, you can delete the original mods after creating the merged one. However, since the merged mod has the highest priority by default and loads last to overwrite conflicts, keeping the originals shouldn't cause any issues.

- ### Where are the installed tools and unpacked vanilla files located?

Those are being placed in the `zonepaq/tools` folder in the same directory as the toolkit.

- ### Can this Toolkit be used for other Unreal Engine games?

Theoretically, yes. You can try and leave your feedback.

- ### Is the ZonePaq Toolkit free?

Yes, this tool is completely free and open source under the MIT License.

## Credits

- Gratitude to the developers of Tkinter, CustomTkinter, and all other libraries utilized in this project.
- A huge thanks to [Sabre](https://next.nexusmods.com/profile/ModsBySabre) for testing and assisting with debugging!
- Special thanks to the respective developers of repak_cli, KDiff3, WinMerge, AESDumpster, and 7z.
- Appreciation to the developers of S.T.A.L.K.E.R. 2.
