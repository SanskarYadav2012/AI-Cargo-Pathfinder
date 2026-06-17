#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sensors.py — Simulated LiDAR / proximity sensor system using Bullet raycasts.
══════════════════════════════════════════════════════════════════════════════

The sensor array casts a fan of rays from the front of the robot into the
Bullet physics world.  Each ray returns:
  • Whether it hit something (bool)
  • The distance to the hit point (float, in metres)
  • The world‑space hit position (Vec3)

The class also provides a convenience ``closest_hit`` property and a method
to render debug lines for the rays.

Design notes
────────────
  • All raycasts go through ``BulletWorld.rayTestClosest`` so they respect
    *every* rigid body in the scene (walls, shelves, crates).
  • The fan angle and number of rays are controlled by constants, making it
    trivial to add more rays or tighten the beam.
  • This module is intentionally decoupled from the robot controller so it
    could be reused with a different agent.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

from panda3d.core import LVector3f, NodePath, Vec3, TransformState
from panda3d.bullet import BulletWorld

# ── Project imports ──
from core.constants import (
    LIDAR_RANGE,
    LIDAR_NUM_RAYS,
    LIDAR_FAN_ANGLE,
    LIDAR_HEIGHT_OFFSET,
    LIDAR_DANGER_DISTANCE,
    COLOR_SENSOR_RAY,
)
from core.procedural_geo import make_line


# ──────────────────────────────────────────────────────────────────────────────
# Data container for a single ray result
# ──────────────────────────────────────────────────────────────────────────────
@dataclass
class RayResult:
    """
    Stores the outcome of a single LiDAR ray.

    Attributes
    ──────────
        angle_deg : The angle of this ray relative to the robot's forward
                    direction (0 = dead‑ahead, negative = left, positive = right).
        has_hit   : True if the ray struck a rigid body.
        distance  : Distance to the hit point (``LIDAR_RANGE`` if no hit).
        hit_pos   : World‑space position of the hit (or ray endpoint if miss).
        is_danger : True if distance < LIDAR_DANGER_DISTANCE.
    """
    angle_deg: float = 0.0
    has_hit: bool = False
    distance: float = LIDAR_RANGE
    hit_pos: LVector3f = field(default_factory=lambda: LVector3f(0, 0, 0))
    is_danger: bool = False


class LidarSensor:
    """
    A fan‑shaped array of Bullet raycasts emitted from a parent NodePath.

    Usage
    ─────
        sensor = LidarSensor(bullet_world, robot_node)
        sensor.update()                       # call once per frame
        for r in sensor.results:
            print(r.distance)
    """

    def __init__(
        self,
        world: BulletWorld,
        parent_np: NodePath,
        render: NodePath,
    ) -> None:
        """
        Parameters
        ──────────
            world     : The Bullet physics world (for rayTestClosest).
            parent_np : The NodePath from which rays originate (the robot body).
            render    : Scene root — debug lines are attached here.
        """
        self._world = world
        self._parent = parent_np
        self._render = render

        # Pre‑compute the angles for each ray in the fan
        half_fan = LIDAR_FAN_ANGLE / 2.0
        if LIDAR_NUM_RAYS > 1:
            step = LIDAR_FAN_ANGLE / (LIDAR_NUM_RAYS - 1)
        else:
            step = 0.0
        self._ray_angles: list[float] = [
            -half_fan + i * step for i in range(LIDAR_NUM_RAYS)
        ]

        # Latest scan results
        self.results: list[RayResult] = [RayResult() for _ in range(LIDAR_NUM_RAYS)]

        # Debug visualisation lines (lazily created)
        self._debug_lines: list[Optional[NodePath]] = [None] * LIDAR_NUM_RAYS
        self._debug_visible: bool = True

    # ──────────────────────────────────────────────────────────────────────
    # Per‑frame scan
    # ──────────────────────────────────────────────────────────────────────
    def update(self) -> None:
        """
        Cast all rays from the robot's current position / heading and
        store the results in ``self.results``.

        This should be called exactly once per frame, *after* physics
        has been stepped.
        """
        # Robot world transform
        robot_pos: LVector3f = self._parent.getPos()
        robot_h: float = self._parent.getH()  # heading in degrees

        # Sensor origin (slightly above robot base)
        origin = LVector3f(
            robot_pos.getX(),
            robot_pos.getY() + LIDAR_HEIGHT_OFFSET,
            robot_pos.getZ(),
        )

        for i, angle_offset in enumerate(self._ray_angles):
            # Absolute angle for this ray (Panda3D heading: 0 = +Y in XZ plane
            # but our forward is -Z when heading=0 in Panda's convention, so we
            # convert properly).
            abs_angle = math.radians(robot_h + angle_offset)

            # Direction vector: in Panda3D's coordinate system, heading 0 with
            # a standard setH means forward is along +X (sin) / -Z (-cos) when
            # rotated around Y.  We need to match the robot's actual forward.
            dx = -math.sin(abs_angle)
            dz = -math.cos(abs_angle)
            direction = LVector3f(dx, 0, dz)

            end_point = origin + direction * LIDAR_RANGE

            # ── Bullet raycast ──
            result = self._world.rayTestClosest(origin, end_point)

            ray = self.results[i]
            ray.angle_deg = angle_offset

            if result.hasHit():
                hit_pt = result.getHitPos()
                dist = (hit_pt - origin).length()
                ray.has_hit = True
                ray.distance = dist
                ray.hit_pos = hit_pt
                ray.is_danger = dist < LIDAR_DANGER_DISTANCE
            else:
                ray.has_hit = False
                ray.distance = LIDAR_RANGE
                ray.hit_pos = end_point
                ray.is_danger = False

            # ── Update debug line ──
            self._update_debug_line(i, origin, ray)

    # ──────────────────────────────────────────────────────────────────────
    # Convenience properties
    # ──────────────────────────────────────────────────────────────────────
    @property
    def closest_hit(self) -> RayResult:
        """Return the ``RayResult`` with the shortest hit distance."""
        return min(self.results, key=lambda r: r.distance)

    @property
    def any_danger(self) -> bool:
        """Return True if *any* ray is within the danger threshold."""
        return any(r.is_danger for r in self.results)

    @property
    def danger_side(self) -> float:
        """
        Return a steering hint:
          •  < 0 → obstacle mainly on the LEFT  → steer RIGHT
          •  > 0 → obstacle mainly on the RIGHT → steer LEFT
          •  ≈ 0 → obstacle dead ahead

        The value is a weighted average of the danger rays' angles,
        inversely weighted by distance (closer = stronger influence).
        """
        weighted_sum = 0.0
        weight_total = 0.0
        for r in self.results:
            if r.is_danger:
                w = 1.0 / max(r.distance, 0.1)
                weighted_sum += r.angle_deg * w
                weight_total += w
        if weight_total < 1e-6:
            return 0.0
        return weighted_sum / weight_total

    # ──────────────────────────────────────────────────────────────────────
    # Debug visualisation
    # ──────────────────────────────────────────────────────────────────────
    def _update_debug_line(self, idx: int, origin: LVector3f, ray: RayResult) -> None:
        """Redraw a single debug ray line."""
        # Remove old line
        if self._debug_lines[idx] is not None:
            self._debug_lines[idx].removeNode()

        if not self._debug_visible:
            self._debug_lines[idx] = None
            return

        # Colour: green if safe, red if danger
        if ray.is_danger:
            color = (1.0, 0.2, 0.15, 0.8)
        elif ray.has_hit:
            color = (1.0, 0.8, 0.1, 0.5)
        else:
            color = (0.2, 1.0, 0.3, 0.3)

        line_np = make_line(
            f"lidar_ray_{idx}",
            start=origin,
            end=ray.hit_pos,
            color=color,
            thickness=1.5,
        )
        line_np.reparentTo(self._render)
        self._debug_lines[idx] = line_np

    def toggle_visibility(self) -> bool:
        """Toggle debug ray visibility. Returns new state."""
        self._debug_visible = not self._debug_visible
        if not self._debug_visible:
            for i in range(len(self._debug_lines)):
                if self._debug_lines[i] is not None:
                    self._debug_lines[i].removeNode()
                    self._debug_lines[i] = None
        return self._debug_visible

    # ──────────────────────────────────────────────────────────────────────
    # Console‑friendly string
    # ──────────────────────────────────────────────────────────────────────
    def format_console_report(self) -> str:
        """Return a compact multi‑line string summarising all rays."""
        lines = ["-- LiDAR Scan --"]
        for r in self.results:
            tag = "!! DANGER" if r.is_danger else ("   hit  " if r.has_hit else "  clear ")
            lines.append(
                f"  Ray {r.angle_deg:+6.1f}° | {tag} | dist={r.distance:5.2f} m"
            )
        return "\n".join(lines)
