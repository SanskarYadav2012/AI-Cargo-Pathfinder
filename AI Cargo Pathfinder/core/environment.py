#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
environment.py — Procedural warehouse geometry + Bullet collision bodies.
══════════════════════════════════════════════════════════════════════════

Builds every piece of the warehouse entirely from code:
  • A thick floor slab with a static Bullet rigid body.
  • Four perimeter walls (also static).
  • Configurable shelf / crate obstacles defined in ``constants.py``.
  • Simple directional + ambient lighting.

All meshes are generated via ``procedural_geo`` — no .egg or .gltf files
are loaded.
"""

from __future__ import annotations

from panda3d.core import (
    AmbientLight,
    DirectionalLight,
    LVector4f,
    NodePath,
    Vec3,
)
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode

# ── Project imports ──
from core.constants import (
    COLOR_CRATE,
    COLOR_FLOOR,
    COLOR_PILLAR,
    COLOR_SHELF,
    COLOR_WALL,
    FLOOR_HALF,
    FLOOR_SIZE,
    FLOOR_THICKNESS,
    SHELF_DEFINITIONS,
    WALL_HEIGHT,
    WALL_THICKNESS,
)
from core.procedural_geo import make_box_mesh


class WarehouseEnvironment:
    """
    Procedurally generated warehouse — floor, walls, obstacles, and lights.

    Parameters
    ──────────
        render       : The scene‑graph root from ShowBase.
        bullet_world : A ``BulletWorld`` instance for physics.
    """

    def __init__(self, render: NodePath, bullet_world) -> None:
        self._render = render
        self._world = bullet_world

        # Keep references so obstacles can be queried later
        self.obstacle_nodes: list[NodePath] = []

        # Build the scene
        self._build_floor()
        self._build_walls()
        self._build_obstacles()
        self._setup_lighting()

    # ──────────────────────────────────────────────────────────────────────
    # Floor
    # ──────────────────────────────────────────────────────────────────────
    def _build_floor(self) -> None:
        """Create a flat concrete slab with a static Bullet body."""
        hx = FLOOR_HALF
        hy = FLOOR_THICKNESS / 2.0
        hz = FLOOR_HALF

        # Visual mesh
        mesh = make_box_mesh("floor_mesh", hx, hy, hz, COLOR_FLOOR)

        # Bullet body (mass = 0 → static)
        shape = BulletBoxShape(Vec3(hx, hy, hz))
        body = BulletRigidBodyNode("floor_body")
        body.addShape(shape)
        body.setMass(0)

        body_np = self._render.attachNewNode(body)
        body_np.setPos(0, -hy, 0)  # top surface sits at Y = 0
        mesh.reparentTo(body_np)

        self._world.attachRigidBody(body)

    # ──────────────────────────────────────────────────────────────────────
    # Perimeter walls
    # ──────────────────────────────────────────────────────────────────────
    def _build_walls(self) -> None:
        """
        Build four perimeter walls around the floor.

        Each wall is a thin box that extends from the floor to WALL_HEIGHT.
        """
        wh = WALL_HEIGHT / 2.0
        wt = WALL_THICKNESS / 2.0
        fl = FLOOR_HALF

        # (position, half_extents) for each wall
        wall_specs: list[tuple[tuple[float, float, float],
                                tuple[float, float, float]]] = [
            # North wall (positive Z edge)
            ((0, wh, fl + wt),  (fl + wt, wh, wt)),
            # South wall (negative Z edge)
            ((0, wh, -(fl + wt)), (fl + wt, wh, wt)),
            # East wall (positive X edge)
            ((fl + wt, wh, 0),  (wt, wh, fl + wt)),
            # West wall (negative X edge)
            ((-(fl + wt), wh, 0), (wt, wh, fl + wt)),
        ]

        for i, (pos, (whx, why, whz)) in enumerate(wall_specs):
            mesh = make_box_mesh(f"wall_mesh_{i}", whx, why, whz, COLOR_WALL)

            shape = BulletBoxShape(Vec3(whx, why, whz))
            body = BulletRigidBodyNode(f"wall_body_{i}")
            body.addShape(shape)
            body.setMass(0)

            body_np = self._render.attachNewNode(body)
            body_np.setPos(*pos)
            mesh.reparentTo(body_np)

            self._world.attachRigidBody(body)
            self.obstacle_nodes.append(body_np)

    # ──────────────────────────────────────────────────────────────────────
    # Obstacles (shelves, crates, pillars)
    # ──────────────────────────────────────────────────────────────────────
    def _build_obstacles(self) -> None:
        """
        Spawn every obstacle from the ``SHELF_DEFINITIONS`` list.

        Each entry is a tuple of (x, centre_y, z, hx, hy, hz).
        Colour is chosen heuristically based on size.
        """
        for idx, (x, cy, z, hx, hy, hz) in enumerate(SHELF_DEFINITIONS):
            # Pick colour by size heuristic
            volume = hx * hy * hz
            if volume < 1.0:
                color = COLOR_CRATE
            elif hx < 1.0 and hz < 1.0:
                color = COLOR_PILLAR
            else:
                color = COLOR_SHELF

            mesh = make_box_mesh(f"obstacle_mesh_{idx}", hx, hy, hz, color)

            shape = BulletBoxShape(Vec3(hx, hy, hz))
            body = BulletRigidBodyNode(f"obstacle_body_{idx}")
            body.addShape(shape)
            body.setMass(0)  # static obstacle

            body_np = self._render.attachNewNode(body)
            body_np.setPos(x, cy, z)
            mesh.reparentTo(body_np)

            self._world.attachRigidBody(body)
            self.obstacle_nodes.append(body_np)

    # ──────────────────────────────────────────────────────────────────────
    # Lighting
    # ──────────────────────────────────────────────────────────────────────
    def _setup_lighting(self) -> None:
        """
        Add a directional sun‑light and a soft ambient fill.

        The directional light simulates overhead warehouse strip‑lighting
        angled from above.  The ambient prevents geometry from being
        pitch‑black on shadowed faces.
        """
        # ── Directional (sun / strip‑light) ──
        d_light = DirectionalLight("warehouse_sun")
        d_light.setColor(LVector4f(0.95, 0.92, 0.85, 1.0))
        d_light_np = self._render.attachNewNode(d_light)
        d_light_np.setHpr(45, -60, 0)
        self._render.setLight(d_light_np)

        # ── Secondary directional (fill) ──
        d_fill = DirectionalLight("warehouse_fill")
        d_fill.setColor(LVector4f(0.35, 0.35, 0.45, 1.0))
        d_fill_np = self._render.attachNewNode(d_fill)
        d_fill_np.setHpr(-135, -30, 0)
        self._render.setLight(d_fill_np)

        # ── Ambient ──
        a_light = AmbientLight("warehouse_ambient")
        a_light.setColor(LVector4f(0.20, 0.20, 0.25, 1.0))
        a_light_np = self._render.attachNewNode(a_light)
        self._render.setLight(a_light_np)
