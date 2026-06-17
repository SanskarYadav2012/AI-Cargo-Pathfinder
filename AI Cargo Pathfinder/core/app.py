#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
app.py — Main Panda3D application for the Autonomous Warehouse Robot Simulation.
═════════════════════════════════════════════════════════════════════════════════

This module subclasses ``ShowBase`` and wires together every subsystem:
  • Bullet physics world (``PhysicsManager``)
  • Procedural warehouse environment (``WarehouseEnvironment``)
  • Robot agent with LiDAR sensors (``RobotController``)
  • On‑screen HUD (``HUD``)
  • Keyboard input bindings
  • Third‑person chase camera

The main game loop is a single Panda3D *task* (``_update``) that runs at
frame rate and delegates to each subsystem in order:
    physics → robot → HUD → camera
"""

from __future__ import annotations

import math
import sys

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import (
    AntialiasAttrib,
    loadPrcFileData,
    LVector3f,
    Vec3,
    WindowProperties,
)

# ── Project imports ──
from core.constants import (
    BACKGROUND_COLOR,
    CAMERA_DISTANCE,
    CAMERA_HEIGHT,
    CAMERA_LOOKAT_OFFSET,
    WINDOW_HEIGHT,
    WINDOW_TITLE,
    WINDOW_WIDTH,
)
from core.environment import WarehouseEnvironment
from core.hud import HUD
from core.physics import PhysicsManager
from core.robot import RobotController


class WarehouseSimulationApp(ShowBase):
    """
    Top‑level Panda3D application.

    Instantiating this class creates the window, builds the scene, and
    starts the main loop.  Call ``app.run()`` to enter the event loop.
    """

    # ──────────────────────────────────────────────────────────────────────
    # Initialisation
    # ──────────────────────────────────────────────────────────────────────
    def __init__(self) -> None:
        # ── Pre‑init engine config via PRC ──
        loadPrcFileData("", f"win-size {WINDOW_WIDTH} {WINDOW_HEIGHT}")
        loadPrcFileData("", f"window-title {WINDOW_TITLE}")
        loadPrcFileData("", "show-frame-rate-meter #t")
        loadPrcFileData("", "sync-video #f")  # uncap FPS for smoother physics
        
        # Determine the absolute path to the icon to support PyInstaller's _MEIPASS
        import os
        base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        icon_path = os.path.join(base_dir, 'icon.ico')
        loadPrcFileData("", f"icon-filename {icon_path}")

        super().__init__()

        # ── Window background colour ──
        self.setBackgroundColor(BACKGROUND_COLOR)

        # ── Enable antialiasing for cleaner edges ──
        self.render.setAntialias(AntialiasAttrib.MAuto)

        # ── Disable Panda3D default camera controls (we do our own) ──
        self.disableMouse()

        # ── Subsystems ──
        self._physics = PhysicsManager(self.render)
        self._environment = WarehouseEnvironment(
            self.render, self._physics.world
        )
        self._robot = RobotController(self.render, self._physics.world)
        self._hud = HUD()

        # ── Input bindings ──
        self._setup_input()

        # ── Console print throttle ──
        self._console_timer: float = 0.0
        self._console_interval: float = 1.0  # seconds between console prints

        # ── Register the main update task ──
        self.taskMgr.add(self._update, "main_update_task")

        print("╔══════════════════════════════════════════════════════════╗")
        print("║  AI Cargo Pathfinder — Warehouse Robot Simulation       ║")
        print("║  Engine: Panda3D + Bullet Physics                       ║")
        print("║  Mode  : AUTONOMOUS (press SPACE to toggle)             ║")
        print("╚══════════════════════════════════════════════════════════╝")

    # ──────────────────────────────────────────────────────────────────────
    # Input
    # ──────────────────────────────────────────────────────────────────────
    def _setup_input(self) -> None:
        """Bind keyboard events to robot control flags and app commands."""

        # ── Movement (press / release pairs) ──
        for key, attr in [
            ("w", "input_forward"), ("arrow_up", "input_forward"),
            ("s", "input_reverse"), ("arrow_down", "input_reverse"),
            ("a", "input_left"),    ("arrow_left", "input_left"),
            ("d", "input_right"),   ("arrow_right", "input_right"),
        ]:
            self.accept(key, self._set_input, [attr, True])
            self.accept(f"{key}-up", self._set_input, [attr, False])

        # ── Commands ──
        self.accept("space", self._toggle_autonomous)
        self.accept("r", self._robot.reset)
        self.accept("f1", self._toggle_debug)
        self.accept("escape", sys.exit)

    def _set_input(self, attr: str, value: bool) -> None:
        """Generic callback to flip a boolean flag on the robot."""
        setattr(self._robot, attr, value)

    def _toggle_autonomous(self) -> None:
        """Switch between autonomous and manual control modes."""
        self._robot.autonomous = not self._robot.autonomous
        mode = "AUTONOMOUS" if self._robot.autonomous else "MANUAL"
        print(f"[APP] Switched to {mode} mode.")

    def _toggle_debug(self) -> None:
        """Toggle Bullet debug wireframes and sensor rays."""
        phys_vis = self._physics.toggle_debug()
        ray_vis = self._robot.sensor.toggle_visibility()
        print(f"[APP] Debug: physics={'ON' if phys_vis else 'OFF'}, "
              f"rays={'ON' if ray_vis else 'OFF'}")

    # ──────────────────────────────────────────────────────────────────────
    # Main update loop (runs every frame)
    # ──────────────────────────────────────────────────────────────────────
    def _update(self, task: Task) -> int:
        """
        Per‑frame update — the heart of the simulation.

        Execution order:
            1. Physics step
            2. Robot update (sensors + control logic)
            3. HUD refresh
            4. Camera follow
            5. Console telemetry (throttled)
        """
        dt: float = globalClock.getDt()

        # 1 — Physics
        self._physics.do_physics(dt)

        # 2 — Robot
        self._robot.update(dt)

        # 3 — HUD
        pos = self._robot.position
        self._hud.update(
            mode_str="AUTONOMOUS" if self._robot.autonomous else "MANUAL",
            state_str=self._robot.auto_state_name,
            speed=self._robot.speed,
            pos=(pos.getX(), pos.getY(), pos.getZ()),
            heading=self._robot.heading_deg,
            ray_results=self._robot.sensor.results,
        )

        # 4 — Camera
        self._update_camera()

        # 5 — Console telemetry (throttled so it doesn't flood)
        self._console_timer += dt
        if self._console_timer >= self._console_interval:
            self._console_timer = 0.0
            report = self._robot.sensor.format_console_report()
            print(report)
            print(f"  Speed: {self._robot.speed:.2f} m/s  "
                  f"Heading: {self._robot.heading_deg:.1f}°  "
                  f"Pos: ({pos.getX():.1f}, {pos.getY():.1f}, {pos.getZ():.1f})")

        return Task.cont

    # ──────────────────────────────────────────────────────────────────────
    # Third‑person camera
    # ──────────────────────────────────────────────────────────────────────
    def _update_camera(self) -> None:
        """
        Position the camera behind and above the robot, looking at a point
        slightly ahead of the robot.

        This gives a comfortable third‑person view that tracks the robot
        as it navigates the warehouse.
        """
        rpos = self._robot.position
        heading_rad = math.radians(self._robot.heading_deg)

        # Camera sits behind the robot
        cam_x = rpos.getX() + math.sin(heading_rad) * CAMERA_DISTANCE
        cam_z = rpos.getZ() + math.cos(heading_rad) * CAMERA_DISTANCE

        self.camera.setPos(cam_x, CAMERA_HEIGHT, cam_z)

        # Look‑at point: slightly ahead of the robot
        look_x = rpos.getX() - math.sin(heading_rad) * CAMERA_LOOKAT_OFFSET
        look_z = rpos.getZ() - math.cos(heading_rad) * CAMERA_LOOKAT_OFFSET

        self.camera.lookAt(
            LVector3f(look_x, rpos.getY() + 1.0, look_z)
        )
