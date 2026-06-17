# Building and Packaging

## Standalone Executable
While Python scripts are excellent for development, distributing a game requires a standalone package that doesn't force the end-user to install Python, pip, or the Panda3D engine.

The project uses **PyInstaller** to compile the entire Python environment, the Panda3D engine, and the game scripts into a single distributable folder containing an `.exe`.

## The Build Script (`build_exe.py`)
The provided `build_exe.py` script automates the complex PyInstaller configuration required for Panda3D:
1. **Hidden Imports**: Panda3D uses heavy dynamic loading for its modules (like `direct.showbase` and `direct.task`). PyInstaller's static analyzer cannot detect these, so the script explicitly lists over 30 required `hidden_imports`.
2. **Data Files**: Panda3D relies on underlying C++ configurations located in an `etc/` folder, and default models in a `models/` folder. The build script dynamically locates the user's Panda3D installation and instructs PyInstaller to copy these directories via the `--add-data` flag.
3. **Application Icon**: The script passes an `--icon` flag to PyInstaller to embed `icon.ico` directly into the generated `AICargoPathfinder.exe`, ensuring the application looks professional in the Windows File Explorer and Taskbar.

## Output
Running `python build_exe.py` generates a `dist/AICargoPathfinder` directory. This directory is entirely self-contained. It contains the `.exe` alongside the bundled Python DLLs and compiled libraries. The entire folder is ~140 MB, and can be zipped and shared with any Windows user.
