#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
physics.py — Bullet physics world initialisation and debug helpers.
═══════════════════════════════════════════════════════════════════

Responsibilities
────────────────
  • Create the BulletWorld and attach it to the Panda3D scene graph.
  • Expose a ``do_physics`` method that the main task calls each frame.
  • Provide a debug‑draw node that can be toggled for visual physics inspection.
"""

# ──────────────────────────────────────────────────────────────────────────────
# Panda3D / Bullet imports
# ──────────────────────────────────────────────────────────────────────────────
from panda3d.bullet import BulletWorld, BulletDebugNode
from panda3d.core import NodePath, Vec3

# ──────────────────────────────────────────────────────────────────────────────
# Project imports
# ──────────────────────────────────────────────────────────────────────────────
from core.constants import GRAVITY, PHYSICS_SUBSTEPS


class PhysicsManager:
    """
    Encapsulates the Bullet physics simulation.

    Attributes
    ──────────
        world : BulletWorld
            The Bullet rigid‑body dynamics world.
        debug_np : NodePath
            A scene‑graph node for Bullet debug wireframe rendering.
    """

    def __init__(self, render: NodePath) -> None:
        """
        Parameters
        ──────────
            render : NodePath
                The top‑level render node from ShowBase so we can attach
                the debug‑draw node.
        """
        # ── Create the Bullet world and set gravity ──
        self.world: BulletWorld = BulletWorld()
        self.world.setGravity(Vec3(0, GRAVITY, 0))

        # ── Debug drawing (off by default) ──
        self._debug_node = BulletDebugNode("BulletDebug")
        self._debug_node.showWireframe(True)
        self._debug_node.showConstraints(True)
        self._debug_node.showBoundingBoxes(False)
        self._debug_node.showNormals(False)

        self.debug_np: NodePath = render.attachNewNode(self._debug_node)
        self.debug_np.hide()  # hidden until user toggles it
        self.world.setDebugNode(self._debug_node)

    # ──────────────────────────────────────────────────────────────────────────
    # Per‑frame update
    # ──────────────────────────────────────────────────────────────────────────
    def do_physics(self, dt: float) -> None:
        """
        Advance the Bullet simulation by *dt* seconds.

        Parameters
        ──────────
            dt : float
                Wall‑clock delta time since last frame (seconds).
        """
        self.world.doPhysics(dt, PHYSICS_SUBSTEPS, 1.0 / 180.0)

    # ──────────────────────────────────────────────────────────────────────────
    # Debug toggle
    # ──────────────────────────────────────────────────────────────────────────
    def toggle_debug(self) -> bool:
        """
        Show or hide the Bullet debug wireframe overlay.

        Returns
        ───────
            bool — ``True`` if debug is now visible, ``False`` otherwise.
        """
        if self.debug_np.isHidden():
            self.debug_np.show()
            return True
        else:
            self.debug_np.hide()
            return False
