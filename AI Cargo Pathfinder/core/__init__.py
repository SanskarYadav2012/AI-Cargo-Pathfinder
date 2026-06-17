# ──────────────────────────────────────────────────────────────────────────────
# core/__init__.py — marks 'core' as a Python package
# ──────────────────────────────────────────────────────────────────────────────
"""
Core package for the Autonomous Warehouse Robot Simulation.

Submodules
──────────
    app.py          — ShowBase application subclass & main game loop
    environment.py  — Procedural warehouse geometry (floor, walls, shelves)
    robot.py        — Robot agent with Bullet rigid‑body and motor controls
    sensors.py      — Simulated LiDAR / proximity sensor system (raycasts)
    physics.py      — Bullet physics world setup and debug‑draw helpers
    hud.py          — On‑screen text HUD for sensor readouts
    constants.py    — Shared tuning constants & colour definitions
"""
