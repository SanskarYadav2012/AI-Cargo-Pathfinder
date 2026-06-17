#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hud.py — On‑screen heads‑up display for real‑time telemetry.
═════════════════════════════════════════════════════════════

Renders live text overlays showing:
  • Current mode (Autonomous / Manual)
  • Robot speed and heading
  • Per‑ray LiDAR distances with colour‑coded danger indicators
  • Active FSM state
  • Brief control reference
"""

from __future__ import annotations

from direct.gui.OnscreenText import OnscreenText
from panda3d.core import LVector4f, TextNode

from core.constants import (
    COLOR_HUD_TEXT,
    COLOR_HUD_WARN,
    HUD_FONT_SIZE,
    HUD_LEFT_MARGIN,
    HUD_LINE_SPACING,
    HUD_TOP,
    LIDAR_NUM_RAYS,
)


class HUD:
    """
    Simple text‑based heads‑up display.

    Call ``update()`` every frame with the latest robot state.
    """

    def __init__(self) -> None:
        """Create all text nodes positioned along the left edge."""

        self._lines: list[OnscreenText] = []

        # ── Title line ──
        self._title = self._make_line(0, "AI CARGO PATHFINDER", scale=0.055)

        # ── Dynamic data lines (we'll update their text each frame) ──
        labels = [
            "Mode :",        # 0
            "State:",        # 1
            "Speed:",        # 2
            "Pos  :",        # 3
            "Head :",        # 4
            "--- LiDAR ---", # 5  (static separator)
        ]
        # Add one line per LiDAR ray
        for i in range(LIDAR_NUM_RAYS):
            labels.append(f"Ray {i}:")

        # Controls footer
        labels.append("")  # spacer
        labels.append("--- Controls ---")
        labels.append("WASD/Arrows : Move")
        labels.append("SPACE       : Auto/Manual")
        labels.append("R           : Reset Robot")
        labels.append("F1          : Toggle Debug")
        labels.append("ESC         : Quit")

        for idx, label in enumerate(labels):
            line = self._make_line(idx + 1, label)
            self._lines.append(line)

        # Indices into self._lines for quick access
        self._idx_mode = 0
        self._idx_state = 1
        self._idx_speed = 2
        self._idx_pos = 3
        self._idx_head = 4
        self._idx_lidar_start = 6  # after the separator at index 5

    # ──────────────────────────────────────────────────────────────────────
    # Factory
    # ──────────────────────────────────────────────────────────────────────
    def _make_line(self, row: int, text: str, scale: float = HUD_FONT_SIZE) -> OnscreenText:
        """Create a left‑aligned OnscreenText at the given row."""
        return OnscreenText(
            text=text,
            pos=(HUD_LEFT_MARGIN, HUD_TOP - row * HUD_LINE_SPACING),
            scale=scale,
            fg=COLOR_HUD_TEXT,
            shadow=(0, 0, 0, 0.7),
            align=TextNode.ALeft,
            mayChange=True,
        )

    # ──────────────────────────────────────────────────────────────────────
    # Per‑frame refresh
    # ──────────────────────────────────────────────────────────────────────
    def update(
        self,
        mode_str: str,
        state_str: str,
        speed: float,
        pos: tuple[float, float, float],
        heading: float,
        ray_results: list,
    ) -> None:
        """
        Refresh every HUD field.

        Parameters
        ──────────
            mode_str    : "AUTONOMOUS" or "MANUAL"
            state_str   : FSM state name (e.g., "DRIVE", "REVERSE", "TURN")
            speed       : Robot speed in m/s
            pos         : (x, y, z) world position
            heading     : Heading in degrees
            ray_results : list of ``RayResult`` from the LiDAR sensor
        """
        self._lines[self._idx_mode].setText(f"Mode : {mode_str}")
        self._lines[self._idx_state].setText(f"State: {state_str}")
        self._lines[self._idx_speed].setText(f"Speed: {speed:5.2f} m/s")
        self._lines[self._idx_pos].setText(
            f"Pos  : ({pos[0]:+6.1f}, {pos[1]:+4.1f}, {pos[2]:+6.1f})"
        )
        self._lines[self._idx_head].setText(f"Head : {heading:5.1f}°")

        # LiDAR rays
        for i, ray in enumerate(ray_results):
            idx = self._idx_lidar_start + i
            if idx >= len(self._lines):
                break

            if ray.is_danger:
                tag = "!! DANGER"
                color = COLOR_HUD_WARN
            elif ray.has_hit:
                tag = "  hit   "
                color = LVector4f(1.0, 0.85, 0.3, 1.0)  # amber
            else:
                tag = "  clear "
                color = LVector4f(0.4, 1.0, 0.5, 1.0)    # green

            self._lines[idx].setText(
                f"  Ray {ray.angle_deg:+6.1f}° | {tag} | {ray.distance:5.2f} m"
            )
            self._lines[idx]["fg"] = color
