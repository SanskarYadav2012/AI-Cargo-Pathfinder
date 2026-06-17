#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robot.py — Autonomous warehouse robot agent with Bullet rigid body.
═══════════════════════════════════════════════════════════════════

The robot is a procedurally generated cylinder (body) with a small cap disc
(directional indicator) that moves through the warehouse using Bullet physics.

Two control modes
─────────────────
  1. **Manual** — WASD / arrow‑key input directly sets velocity.
  2. **Autonomous** — a finite‑state machine (DRIVE → REVERSE → TURN → DRIVE)
     reacts to the LiDAR sensor readings.

The ``RobotController`` class owns the Bullet rigid body, visual mesh, and
the ``LidarSensor`` instance.  The main app simply calls ``robot.update(dt)``
each frame.
"""

from __future__ import annotations

import enum
import math
from typing import Optional

from panda3d.core import LVector3f, LVector4f, NodePath, Vec3
from panda3d.bullet import BulletCylinderShape, BulletRigidBodyNode, ZUp, YUp

# ── Project imports ──
from core.constants import (
    COLOR_ROBOT_BODY,
    COLOR_ROBOT_TOP,
    ROBOT_ANGULAR_DAMPING,
    ROBOT_FORWARD_SPEED,
    ROBOT_HEIGHT,
    ROBOT_LINEAR_DAMPING,
    ROBOT_MASS,
    ROBOT_RADIUS,
    ROBOT_REVERSE_SPEED,
    ROBOT_START_HEADING,
    ROBOT_START_POS,
    ROBOT_TURN_RATE,
    AUTO_REVERSE_DURATION,
    AUTO_TURN_DURATION,
    AUTO_TURN_DIRECTION_BIAS,
)
from core.procedural_geo import make_cylinder_mesh, make_box_mesh
from core.sensors import LidarSensor


# ──────────────────────────────────────────────────────────────────────────────
# Autonomous FSM states
# ──────────────────────────────────────────────────────────────────────────────
class _AutoState(enum.Enum):
    """States for the simple obstacle‑avoidance finite‑state machine."""
    DRIVE = "DRIVE"
    REVERSE = "REVERSE"
    TURN = "TURN"


class RobotController:
    """
    Warehouse robot agent.

    Attributes
    ──────────
        node       : NodePath — root of the robot's scene‑graph subtree.
        body       : BulletRigidBodyNode — the physics body.
        sensor     : LidarSensor — forward‑facing proximity scanner.
        autonomous : bool — whether auto‑drive is active.
    """

    def __init__(
        self,
        render: NodePath,
        bullet_world,
    ) -> None:
        """
        Build the robot mesh, physics body, and sensor array.

        Parameters
        ──────────
            render       : Scene‑graph root.
            bullet_world : BulletWorld for collision.
        """
        self._render = render
        self._world = bullet_world

        # ── Visual mesh: body cylinder ──
        body_mesh = make_cylinder_mesh(
            "robot_body_mesh",
            radius=ROBOT_RADIUS,
            height=ROBOT_HEIGHT,
            color=COLOR_ROBOT_BODY,
            segments=24,
        )

        # ── Visual mesh: directional indicator cap ──
        cap_mesh = make_box_mesh(
            "robot_cap_mesh",
            hx=ROBOT_RADIUS * 0.3,
            hy=0.08,
            hz=ROBOT_RADIUS * 0.6,
            color=COLOR_ROBOT_TOP,
        )
        cap_mesh.setPos(0, ROBOT_HEIGHT / 2.0 + 0.08, -ROBOT_RADIUS * 0.35)

        # ── Bullet rigid body ──
        shape = BulletCylinderShape(ROBOT_RADIUS, ROBOT_HEIGHT, YUp)
        self.body = BulletRigidBodyNode("robot_body")
        self.body.addShape(shape)
        self.body.setMass(ROBOT_MASS)
        self.body.setLinearDamping(ROBOT_LINEAR_DAMPING)
        self.body.setAngularDamping(ROBOT_ANGULAR_DAMPING)
        # Lock rotation to Y‑axis only (prevent tipping over)
        self.body.setAngularFactor(Vec3(0, 1, 0))

        # Attach to scene
        self.node: NodePath = render.attachNewNode(self.body)
        self.node.setPos(*ROBOT_START_POS)
        self.node.setH(ROBOT_START_HEADING)

        body_mesh.reparentTo(self.node)
        cap_mesh.reparentTo(self.node)

        self._world.attachRigidBody(self.body)

        # ── Sensor ──
        self.sensor = LidarSensor(self._world, self.node, self._render)

        # ── Control state ──
        self.autonomous: bool = True
        self._auto_state: _AutoState = _AutoState.DRIVE
        self._state_timer: float = 0.0
        self._turn_direction: float = AUTO_TURN_DIRECTION_BIAS

        # Manual input flags (set by key events in app.py)
        self.input_forward: bool = False
        self.input_reverse: bool = False
        self.input_left: bool = False
        self.input_right: bool = False

    # ──────────────────────────────────────────────────────────────────────
    # Per‑frame update
    # ──────────────────────────────────────────────────────────────────────
    def update(self, dt: float) -> None:
        """
        Called every frame by the main task.

        1. Updates the LiDAR sensor.
        2. Runs either autonomous or manual control logic.
        3. Prints a sensor report to the console (throttled).
        """
        # ── 1. Sensor sweep ──
        self.sensor.update()

        # ── 2. Control ──
        if self.autonomous:
            self._run_autonomous(dt)
        else:
            self._run_manual(dt)

        # Clamp vertical velocity to prevent slow drift from numerical error
        vel = self.body.getLinearVelocity()
        if abs(vel.getY()) > 0.05:
            self.body.setLinearVelocity(Vec3(vel.getX(), 0, vel.getZ()))

    # ──────────────────────────────────────────────────────────────────────
    # Autonomous finite‑state machine
    # ──────────────────────────────────────────────────────────────────────
    def _run_autonomous(self, dt: float) -> None:
        """
        Simple three‑state obstacle avoidance:

            DRIVE ──▶ (danger detected) ──▶ REVERSE ──▶ TURN ──▶ DRIVE
        """
        if self._auto_state == _AutoState.DRIVE:
            self._apply_forward(ROBOT_FORWARD_SPEED)

            if self.sensor.any_danger:
                # Transition → REVERSE
                self._auto_state = _AutoState.REVERSE
                self._state_timer = AUTO_REVERSE_DURATION

                # Decide turn direction: steer *away* from the obstacle
                danger = self.sensor.danger_side
                self._turn_direction = -1.0 if danger >= 0 else 1.0

                print(f"[AUTO] Obstacle detected! Reversing. "
                      f"(closest: {self.sensor.closest_hit.distance:.2f} m)")

        elif self._auto_state == _AutoState.REVERSE:
            self._apply_forward(-ROBOT_REVERSE_SPEED)
            self._state_timer -= dt

            if self._state_timer <= 0:
                self._auto_state = _AutoState.TURN
                self._state_timer = AUTO_TURN_DURATION

        elif self._auto_state == _AutoState.TURN:
            self._apply_turn(self._turn_direction)
            self._state_timer -= dt

            if self._state_timer <= 0:
                self._auto_state = _AutoState.DRIVE
                print("[AUTO] Resuming forward drive.")

    # ──────────────────────────────────────────────────────────────────────
    # Manual control
    # ──────────────────────────────────────────────────────────────────────
    def _run_manual(self, dt: float) -> None:
        """Apply manual WASD input."""
        if self.input_forward:
            self._apply_forward(ROBOT_FORWARD_SPEED)
        elif self.input_reverse:
            self._apply_forward(-ROBOT_REVERSE_SPEED)

        if self.input_left:
            self._apply_turn(1.0)
        elif self.input_right:
            self._apply_turn(-1.0)

    # ──────────────────────────────────────────────────────────────────────
    # Low‑level movement helpers
    # ──────────────────────────────────────────────────────────────────────
    def _apply_forward(self, speed: float) -> None:
        """
        Push the robot forward (or backward if speed < 0) along its heading.

        We set the linear velocity directly rather than applying a force,
        which gives crisp, predictable movement suitable for a simulation
        demo.
        """
        heading_rad = math.radians(self.node.getH())
        dx = -math.sin(heading_rad) * speed
        dz = -math.cos(heading_rad) * speed

        self.body.setLinearVelocity(Vec3(dx, 0, dz))

    def _apply_turn(self, direction: float) -> None:
        """
        Rotate the robot around the Y axis.

        Parameters
        ──────────
            direction : +1 = counter‑clockwise (left), −1 = clockwise (right).
        """
        omega = direction * math.radians(ROBOT_TURN_RATE)
        self.body.setAngularVelocity(Vec3(0, omega, 0))

    # ──────────────────────────────────────────────────────────────────────
    # Reset
    # ──────────────────────────────────────────────────────────────────────
    def reset(self) -> None:
        """Teleport the robot back to its starting position and heading."""
        self.body.setLinearVelocity(Vec3(0, 0, 0))
        self.body.setAngularVelocity(Vec3(0, 0, 0))
        self.node.setPos(*ROBOT_START_POS)
        self.node.setH(ROBOT_START_HEADING)
        self._auto_state = _AutoState.DRIVE
        self._state_timer = 0.0
        print("[ROBOT] Position reset.")

    # ──────────────────────────────────────────────────────────────────────
    # State queries (used by the HUD)
    # ──────────────────────────────────────────────────────────────────────
    @property
    def speed(self) -> float:
        """Current scalar speed (m/s)."""
        v = self.body.getLinearVelocity()
        return math.sqrt(v.getX() ** 2 + v.getZ() ** 2)

    @property
    def heading_deg(self) -> float:
        """Current heading in degrees."""
        return self.node.getH() % 360

    @property
    def position(self) -> LVector3f:
        """Current world position."""
        return self.node.getPos()

    @property
    def auto_state_name(self) -> str:
        """Current autonomous FSM state as a string."""
        return self._auto_state.value
