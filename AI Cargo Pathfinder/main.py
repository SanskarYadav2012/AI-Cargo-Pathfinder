#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          AUTONOMOUS WAREHOUSE ROBOT SIMULATION — Main Entry Point          ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Author  : AI Cargo Pathfinder Team                                        ║
║  Engine  : Panda3D 1.10+ with Bullet Physics                               ║
║  Python  : 3.10+                                                           ║
║  License : MIT                                                             ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Description:                                                              ║
║  A fully procedural 3D warehouse simulation featuring:                     ║
║    • Bullet‑physics rigid‑body collisions (robot vs. walls & shelves)      ║
║    • Simulated LiDAR / proximity sensors via Bullet raycasts               ║
║    • Reactive obstacle‑avoidance behaviour (reverse + steer)               ║
║    • On‑screen HUD with real‑time sensor readouts                          ║
║    • Zero external assets — every mesh is generated in code                ║
╚══════════════════════════════════════════════════════════════════════════════╝

Usage
─────
    python main.py

Controls (Debug / Override)
───────────────────────────
    W / Up Arrow    — Manual forward thrust
    S / Down Arrow  — Manual reverse thrust
    A / Left Arrow  — Steer left
    D / Right Arrow — Steer right
    SPACE           — Toggle autonomous mode on / off
    R               — Reset robot to starting position
    ESC             — Quit the simulation
"""

# ──────────────────────────────────────────────────────────────────────────────
# Standard-library imports
# ──────────────────────────────────────────────────────────────────────────────
import sys
import os

# ──────────────────────────────────────────────────────────────────────────────
# Force UTF-8 on Windows console to prevent UnicodeEncodeError (cp1252).
# This must happen before ANY print() call in the entire application.
# ──────────────────────────────────────────────────────────────────────────────
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ──────────────────────────────────────────────────────────────────────────────
# Ensure the project root is on sys.path so sibling packages resolve cleanly
# ──────────────────────────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ──────────────────────────────────────────────────────────────────────────────
# Application entry‑point
# ──────────────────────────────────────────────────────────────────────────────
from core.app import WarehouseSimulationApp  # noqa: E402 — path setup above


def main() -> None:
    """Instantiate and run the Panda3D application."""
    app = WarehouseSimulationApp()
    app.run()


if __name__ == "__main__":
    main()
