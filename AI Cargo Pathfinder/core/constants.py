#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
constants.py — Shared tuning constants and colour definitions.
═══════════════════════════════════════════════════════════════

All magic numbers live here so the rest of the codebase stays clean and every
tuneable can be adjusted from a single file.
"""

from panda3d.core import LVector4f

# ──────────────────────────────────────────────────────────────────────────────
# Window & rendering
# ──────────────────────────────────────────────────────────────────────────────
WINDOW_TITLE: str = "AI Cargo Pathfinder — Autonomous Warehouse Robot Simulation"
WINDOW_WIDTH: int = 1280
WINDOW_HEIGHT: int = 720
BACKGROUND_COLOR: LVector4f = LVector4f(0.08, 0.08, 0.12, 1.0)  # dark blue‑grey

# ──────────────────────────────────────────────────────────────────────────────
# Physics (Bullet)
# ──────────────────────────────────────────────────────────────────────────────
GRAVITY: float = -9.81            # m/s²  (negative Y is down)
PHYSICS_SUBSTEPS: int = 10        # Bullet sub‑steps per frame

# ──────────────────────────────────────────────────────────────────────────────
# Warehouse floor dimensions (units ≈ metres)
# ──────────────────────────────────────────────────────────────────────────────
FLOOR_SIZE: float = 40.0          # total floor side‑length
FLOOR_HALF: float = FLOOR_SIZE / 2.0
FLOOR_THICKNESS: float = 0.5     # visual slab thickness
WALL_HEIGHT: float = 4.0          # perimeter wall height
WALL_THICKNESS: float = 0.5      # perimeter wall thickness

# ──────────────────────────────────────────────────────────────────────────────
# Obstacle / shelf layout
# ──────────────────────────────────────────────────────────────────────────────
# Each entry: (x, y_ground, z, half_extents_x, half_extents_y, half_extents_z)
# y_ground is the height off the floor to the *centre* of the box.
SHELF_DEFINITIONS: list[tuple[float, float, float, float, float, float]] = [
    # ── Row 1: Two long shelving units ──
    (-12.0, 1.5, -8.0,   4.0, 1.5, 1.0),
    (-12.0, 1.5,  8.0,   4.0, 1.5, 1.0),
    # ── Row 2: Two medium boxes ──
    (  0.0, 1.0,  -5.0,  1.5, 1.0, 1.5),
    (  0.0, 1.0,   5.0,  1.5, 1.0, 1.5),
    # ── Row 3: Two long shelving units ──
    ( 12.0, 1.5, -8.0,   4.0, 1.5, 1.0),
    ( 12.0, 1.5,  8.0,   4.0, 1.5, 1.0),
    # ── Scattered single crates ──
    ( -6.0, 0.75,  0.0,  0.75, 0.75, 0.75),
    (  6.0, 0.75,  0.0,  0.75, 0.75, 0.75),
    (  0.0, 0.75, -14.0, 0.75, 0.75, 0.75),
    (  0.0, 0.75,  14.0, 0.75, 0.75, 0.75),
    # ── Central pillar ──
    (  0.0, 2.0,   0.0,  0.5,  2.0,  0.5),
]

# ──────────────────────────────────────────────────────────────────────────────
# Robot physical properties
# ──────────────────────────────────────────────────────────────────────────────
ROBOT_RADIUS: float = 0.6        # cylinder radius
ROBOT_HEIGHT: float = 1.2        # cylinder full height
ROBOT_MASS: float = 80.0         # kg
ROBOT_START_POS: tuple[float, float, float] = (-16.0, 1.0, -16.0)
ROBOT_START_HEADING: float = 45.0  # degrees — faces towards centre

# ──────────────────────────────────────────────────────────────────────────────
# Robot movement tuning
# ──────────────────────────────────────────────────────────────────────────────
ROBOT_FORWARD_SPEED: float = 6.0   # m/s
ROBOT_REVERSE_SPEED: float = 3.0   # m/s
ROBOT_TURN_RATE: float = 90.0      # degrees/s
ROBOT_LINEAR_DAMPING: float = 0.6  # Bullet linear damping
ROBOT_ANGULAR_DAMPING: float = 0.9 # Bullet angular damping

# ──────────────────────────────────────────────────────────────────────────────
# Sensor (LiDAR) configuration
# ──────────────────────────────────────────────────────────────────────────────
LIDAR_RANGE: float = 12.0         # max raycast distance (metres)
LIDAR_NUM_RAYS: int = 7           # total rays in the fan
LIDAR_FAN_ANGLE: float = 120.0    # total fan spread (degrees)
LIDAR_HEIGHT_OFFSET: float = 0.6  # sensor mount height above robot base
LIDAR_DANGER_DISTANCE: float = 2.5  # threshold to trigger avoidance (metres)

# ──────────────────────────────────────────────────────────────────────────────
# Autonomous‑mode behaviour
# ──────────────────────────────────────────────────────────────────────────────
AUTO_REVERSE_DURATION: float = 0.6   # seconds to reverse after detection
AUTO_TURN_DURATION: float = 0.8      # seconds to turn after reversing
AUTO_TURN_DIRECTION_BIAS: float = 1.0  # +1 = prefer right, −1 = prefer left

# ──────────────────────────────────────────────────────────────────────────────
# Colour palette (RGBA floats)
# ──────────────────────────────────────────────────────────────────────────────
COLOR_FLOOR      = LVector4f(0.25, 0.27, 0.30, 1.0)   # concrete grey
COLOR_WALL       = LVector4f(0.35, 0.30, 0.25, 1.0)   # dark brown
COLOR_SHELF      = LVector4f(0.85, 0.55, 0.15, 1.0)   # warehouse orange
COLOR_CRATE      = LVector4f(0.60, 0.45, 0.20, 1.0)   # cardboard tan
COLOR_PILLAR     = LVector4f(0.50, 0.50, 0.55, 1.0)   # steel grey
COLOR_ROBOT_BODY = LVector4f(0.15, 0.55, 0.90, 1.0)   # bright blue
COLOR_ROBOT_TOP  = LVector4f(0.10, 0.80, 0.35, 1.0)   # green indicator cap
COLOR_SENSOR_RAY = LVector4f(1.00, 0.25, 0.25, 0.6)   # red laser line
COLOR_HUD_TEXT   = LVector4f(0.90, 0.95, 1.00, 1.0)   # near‑white
COLOR_HUD_WARN   = LVector4f(1.00, 0.35, 0.20, 1.0)   # warning red

# ──────────────────────────────────────────────────────────────────────────────
# HUD layout
# ──────────────────────────────────────────────────────────────────────────────
HUD_FONT_SIZE: float = 0.045
HUD_LINE_SPACING: float = 0.055
HUD_LEFT_MARGIN: float = -1.25
HUD_TOP: float = 0.95

# ──────────────────────────────────────────────────────────────────────────────
# Camera
# ──────────────────────────────────────────────────────────────────────────────
CAMERA_DISTANCE: float = 18.0     # distance behind/above robot
CAMERA_HEIGHT: float = 14.0       # height above ground
CAMERA_LOOKAT_OFFSET: float = 5.0 # look‑at point ahead of robot
