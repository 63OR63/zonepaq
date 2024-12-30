# Changelog

## [2.0-rc.2] - 2024-12-30

- Reimplemented `Ctrl+V` and `Delete` keyboard actions for listboxes
- Introduced an `Open file` dialogue on click for DnD labels
- Adjusted spacing in `Settings` menu
- Bug fix: Removed excess param in copy method calls

## [2.0-rc.1] - 2024-12-29

**GUI:**

- Rebuilt the GUI using CustomTkinter
- Introduced drag-and-drop functionality
- Implemented a new theme engine with light/dark mode options
- Enhanced user experience and interface

**Backend:**

- Added auto-installation of repak cli, KDiff3, WinMerge, AESDumpster, 7zr
- Added auto-detection of AES encryption key
- Added auto-extraction and cleaning of vanilla game archives
- Added auto-detection of Game Pass installation
- Refactored the entire backend
- Fixed bugs

## [1.3.1] - 2024-12-13

- Refactored config loader
- Fixed crash on start if settings.ini doesn't contain all variables

## [1.3] - 2024-12-12

- Implemented validation for settings values
- Improved message boxes to notify users of improperly set executable paths
- Refactored parts of code
- Fixed bugs

## [1.2] - 2024-12-12

- Added ability to unpack encrypted vanilla files
- Improved GUI
- Fixed bugs

## [1.1] - 2024-12-11

- Calls to repak are now asynchronous, increasing operational speed
- Tree in conflict resolver is now sorted alphabetically
- Fixed miscellaneous bugs

## [1.0.2] - 2024-12-11

- Added messagebox notifications when the conflict resolver fails to process any selected files.
- Enabled saving logs to the ./logs directory.

## [1.0.1] - 2024-12-10

- Fixed a bug repacking merged file with a forced destination.

## [1.0] - 2024-12-10

- Initial release.
