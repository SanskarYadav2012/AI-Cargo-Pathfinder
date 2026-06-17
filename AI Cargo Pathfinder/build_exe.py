#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_exe.py -- Build a standalone Windows .exe using PyInstaller.
===================================================================

This script automates the PyInstaller build process to produce either:
  - A one-directory distributable (faster startup, easier to debug)
  - A single-file .exe       (easier to share, slower first launch)

Prerequisites
-------------
    pip install pyinstaller

Usage
-----
    python build_exe.py                 # one-directory build (default)
    python build_exe.py --onefile       # single .exe build
    python build_exe.py --console       # keep console window visible
"""

import os
import subprocess
import sys
import argparse
import shutil


def find_panda3d_path() -> str:
    """Locate the panda3d package directory for hidden-import discovery."""
    import panda3d
    return os.path.dirname(panda3d.__file__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build AI Cargo Pathfinder standalone .exe"
    )
    parser.add_argument(
        "--onefile",
        action="store_true",
        help="Produce a single .exe instead of a directory distribution.",
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Keep the console window visible (useful for debug prints).",
    )
    args = parser.parse_args()

    project_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(project_dir, "main.py")
    dist_dir = os.path.join(project_dir, "dist")
    build_dir = os.path.join(project_dir, "build")

    # Clean previous builds
    for d in [dist_dir, build_dir]:
        if os.path.exists(d):
            shutil.rmtree(d, ignore_errors=True)
            print(f"  Cleaned: {d}")

    # Find panda3d installation for data files
    panda3d_path = find_panda3d_path()
    print(f"  Panda3D path: {panda3d_path}")

    # ---- Build the PyInstaller command ----
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name", "AICargoPathfinder",
        "--distpath", dist_dir,
        "--workpath", build_dir,
        "--specpath", project_dir,
        "--icon", "icon.ico",
        "--noconfirm",
        "--clean",
    ]

    # One-file vs one-directory
    if args.onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")

    # Console vs windowed (default: console so sensor prints are visible)
    if args.console:
        cmd.append("--console")
    else:
        cmd.append("--console")  # keep console for sensor readout

    # ---- Hidden imports needed by Panda3D ----
    # Panda3D dynamically loads many modules at runtime which PyInstaller
    # cannot detect via static analysis.  We explicitly list them.
    hidden_imports = [
        "panda3d",
        "panda3d.core",
        "panda3d.bullet",
        "panda3d.direct",
        "panda3d.physics",
        "panda3d.egg",
        "direct",
        "direct.showbase",
        "direct.showbase.ShowBase",
        "direct.task",
        "direct.task.Task",
        "direct.gui",
        "direct.gui.OnscreenText",
        "direct.gui.DirectGui",
        "direct.directnotify",
        "direct.directnotify.DirectNotify",
        "direct.interval",
        "direct.showbase.Loader",
        "direct.showbase.Audio3DManager",
        "direct.particles",
        "core",
        "core.app",
        "core.constants",
        "core.environment",
        "core.hud",
        "core.physics",
        "core.procedural_geo",
        "core.robot",
        "core.sensors",
    ]

    for imp in hidden_imports:
        cmd.extend(["--hidden-import", imp])

    # ---- Collect Panda3D data files (etc/, models/) ----
    # Panda3D needs its 'etc/' config files and 'models/' directory at runtime
    panda3d_etc = os.path.join(panda3d_path, "..", "etc")
    panda3d_models = os.path.join(panda3d_path, "..", "models")

    if os.path.isdir(panda3d_etc):
        cmd.extend(["--add-data", f"{os.path.abspath(panda3d_etc)}{os.pathsep}etc"])
    if os.path.isdir(panda3d_models):
        cmd.extend(["--add-data", f"{os.path.abspath(panda3d_models)}{os.pathsep}models"])

    # Add the panda3d package itself
    cmd.extend(["--collect-all", "panda3d"])
    cmd.extend(["--collect-all", "direct"])
    
    # Add the app icon
    cmd.extend(["--add-data", f"icon.ico{os.pathsep}."])

    # ---- Entry point ----
    cmd.append(main_script)

    print()
    print("=" * 70)
    print("  Building AI Cargo Pathfinder executable...")
    print("=" * 70)
    print(f"  Command: {' '.join(cmd[:8])} ...")
    print()

    result = subprocess.run(cmd, cwd=project_dir)

    if result.returncode == 0:
        print()
        print("=" * 70)
        print("  BUILD SUCCEEDED!")
        print("=" * 70)
        if args.onefile:
            exe_path = os.path.join(dist_dir, "AICargoPathfinder.exe")
        else:
            exe_path = os.path.join(dist_dir, "AICargoPathfinder", "AICargoPathfinder.exe")
        print(f"  Executable: {exe_path}")
        print(f"  Output dir: {dist_dir}")
        print()
        print("  Run with: " + exe_path)
        print("=" * 70)
    else:
        print()
        print("  BUILD FAILED. Check the output above for errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
