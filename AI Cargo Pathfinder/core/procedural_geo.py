#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
procedural_geo.py — Helper functions for generating procedural 3D geometry.
═══════════════════════════════════════════════════════════════════════════════

Panda3D's built‑in primitives (via ``loader.loadModel("misc/…")``) require a
default model repository to be present.  To guarantee the simulation works on
*any* fresh Python + Panda3D install with zero external files, we build our
meshes from raw ``GeomVertexData`` / ``GeomTriangles``.

Public API
──────────
    make_box_mesh(name, hx, hy, hz, color) → NodePath
    make_cylinder_mesh(name, radius, height, color, segments) → NodePath
    make_line(name, start, end, color, thickness) → NodePath
"""

from __future__ import annotations

import math
from typing import Sequence

from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    LVector3f,
    LVector4f,
    NodePath,
    LineSegs,
)


# ══════════════════════════════════════════════════════════════════════════════
# BOX (axis‑aligned rectangular prism)
# ══════════════════════════════════════════════════════════════════════════════

def make_box_mesh(
    name: str,
    hx: float,
    hy: float,
    hz: float,
    color: LVector4f | Sequence[float] = (1, 1, 1, 1),
) -> NodePath:
    """
    Create a coloured, axis‑aligned box centred at the origin.

    Parameters
    ──────────
        name  : Human‑readable node name.
        hx,hy,hz : Half‑extents along X, Y, Z.
        color : RGBA tuple or LVector4f.

    Returns
    ───────
        NodePath wrapping a GeomNode of the box.
    """
    # Eight corners of the box
    verts = [
        (-hx, -hy, -hz),
        ( hx, -hy, -hz),
        ( hx,  hy, -hz),
        (-hx,  hy, -hz),
        (-hx, -hy,  hz),
        ( hx, -hy,  hz),
        ( hx,  hy,  hz),
        (-hx,  hy,  hz),
    ]

    # 12 triangles (2 per face, 6 faces), indices into *verts*
    tris = [
        # bottom (Y = -hy)
        (0, 1, 5), (0, 5, 4),
        # top    (Y = +hy)
        (3, 6, 2), (3, 7, 6),
        # front  (Z = +hz)
        (4, 5, 6), (4, 6, 7),
        # back   (Z = -hz)
        (1, 0, 3), (1, 3, 2),
        # left   (X = -hx)
        (0, 4, 7), (0, 7, 3),
        # right  (X = +hx)
        (5, 1, 2), (5, 2, 6),
    ]

    # Face normals (one per pair of triangles)
    normals = [
        ( 0, -1,  0), ( 0, -1,  0),
        ( 0,  1,  0), ( 0,  1,  0),
        ( 0,  0,  1), ( 0,  0,  1),
        ( 0,  0, -1), ( 0,  0, -1),
        (-1,  0,  0), (-1,  0,  0),
        ( 1,  0,  0), ( 1,  0,  0),
    ]

    # Build vertex data — we duplicate verts per triangle so each face can
    # have its own normal (flat shading).
    fmt = GeomVertexFormat.getV3n3c4()
    vdata = GeomVertexData(name, fmt, Geom.UHStatic)
    vdata.setNumRows(len(tris) * 3)

    v_writer = GeomVertexWriter(vdata, "vertex")
    n_writer = GeomVertexWriter(vdata, "normal")
    c_writer = GeomVertexWriter(vdata, "color")

    prim = GeomTriangles(Geom.UHStatic)

    idx = 0
    for tri_idx, (a, b, c) in enumerate(tris):
        nx, ny, nz = normals[tri_idx]
        for vi in (a, b, c):
            vx, vy, vz = verts[vi]
            v_writer.addData3(vx, vy, vz)
            n_writer.addData3(nx, ny, nz)
            c_writer.addData4(*color)
            prim.addVertex(idx)
            idx += 1

    prim.closePrimitive()

    geom = Geom(vdata)
    geom.addPrimitive(prim)

    geom_node = GeomNode(name)
    geom_node.addGeom(geom)
    return NodePath(geom_node)


# ══════════════════════════════════════════════════════════════════════════════
# CYLINDER (upright along Y axis)
# ══════════════════════════════════════════════════════════════════════════════

def make_cylinder_mesh(
    name: str,
    radius: float,
    height: float,
    color: LVector4f | Sequence[float] = (1, 1, 1, 1),
    segments: int = 24,
) -> NodePath:
    """
    Create a closed cylinder centred at the origin, oriented along Y.

    The mesh consists of:
      • A tube (side wall) of *segments* quads
      • A top disc and a bottom disc (triangle fans)

    Parameters
    ──────────
        name     : Node name.
        radius   : Cylinder radius.
        height   : Total height (extends ±height/2 along Y).
        color    : RGBA tuple.
        segments : Number of longitudinal slices (≥ 6).

    Returns
    ───────
        NodePath wrapping the cylinder GeomNode.
    """
    segments = max(segments, 6)
    half_h = height / 2.0

    fmt = GeomVertexFormat.getV3n3c4()
    vdata = GeomVertexData(name, fmt, Geom.UHStatic)

    v_writer = GeomVertexWriter(vdata, "vertex")
    n_writer = GeomVertexWriter(vdata, "normal")
    c_writer = GeomVertexWriter(vdata, "color")

    prim = GeomTriangles(Geom.UHStatic)

    idx = 0  # running vertex index

    # ── Side wall ─────────────────────────────────────────────────────────
    for i in range(segments):
        theta0 = 2.0 * math.pi * i / segments
        theta1 = 2.0 * math.pi * ((i + 1) % segments) / segments

        x0, z0 = math.cos(theta0) * radius, math.sin(theta0) * radius
        x1, z1 = math.cos(theta1) * radius, math.sin(theta1) * radius

        # Normal for the quad (average of the two edge normals is fine for
        # a cylinder — they point radially outward).
        nx0, nz0 = math.cos(theta0), math.sin(theta0)
        nx1, nz1 = math.cos(theta1), math.sin(theta1)

        # Four vertices of the quad (two triangles)
        quad_verts = [
            (x0, -half_h, z0, nx0, 0, nz0),
            (x1, -half_h, z1, nx1, 0, nz1),
            (x1,  half_h, z1, nx1, 0, nz1),
            (x0,  half_h, z0, nx0, 0, nz0),
        ]
        for vx, vy, vz, nvx, nvy, nvz in quad_verts:
            v_writer.addData3(vx, vy, vz)
            n_writer.addData3(nvx, nvy, nvz)
            c_writer.addData4(*color)

        # Two triangles for this quad
        prim.addVertices(idx + 0, idx + 1, idx + 2)
        prim.addVertices(idx + 0, idx + 2, idx + 3)
        idx += 4

    # ── Top cap ───────────────────────────────────────────────────────────
    centre_top = idx
    v_writer.addData3(0, half_h, 0)
    n_writer.addData3(0, 1, 0)
    c_writer.addData4(*color)
    idx += 1

    top_ring_start = idx
    for i in range(segments):
        theta = 2.0 * math.pi * i / segments
        v_writer.addData3(math.cos(theta) * radius, half_h, math.sin(theta) * radius)
        n_writer.addData3(0, 1, 0)
        c_writer.addData4(*color)
        idx += 1

    for i in range(segments):
        next_i = (i + 1) % segments
        prim.addVertices(centre_top, top_ring_start + i, top_ring_start + next_i)

    # ── Bottom cap ────────────────────────────────────────────────────────
    centre_bot = idx
    v_writer.addData3(0, -half_h, 0)
    n_writer.addData3(0, -1, 0)
    c_writer.addData4(*color)
    idx += 1

    bot_ring_start = idx
    for i in range(segments):
        theta = 2.0 * math.pi * i / segments
        v_writer.addData3(math.cos(theta) * radius, -half_h, math.sin(theta) * radius)
        n_writer.addData3(0, -1, 0)
        c_writer.addData4(*color)
        idx += 1

    for i in range(segments):
        next_i = (i + 1) % segments
        # Winding order reversed so normals face downward
        prim.addVertices(centre_bot, bot_ring_start + next_i, bot_ring_start + i)

    prim.closePrimitive()

    geom = Geom(vdata)
    geom.addPrimitive(prim)
    geom_node = GeomNode(name)
    geom_node.addGeom(geom)
    return NodePath(geom_node)


# ══════════════════════════════════════════════════════════════════════════════
# LINE SEGMENT (for visualising sensor rays)
# ══════════════════════════════════════════════════════════════════════════════

def make_line(
    name: str,
    start: LVector3f | tuple[float, float, float],
    end: LVector3f | tuple[float, float, float],
    color: LVector4f | Sequence[float] = (1, 0, 0, 1),
    thickness: float = 2.0,
) -> NodePath:
    """
    Draw a single coloured line segment.

    Parameters
    ──────────
        name      : Node name.
        start/end : 3‑component world positions.
        color     : RGBA colour.
        thickness : Pixel width of the line.

    Returns
    ───────
        NodePath that can be reparented and repositioned.
    """
    ls = LineSegs(name)
    ls.setThickness(thickness)
    ls.setColor(*color)
    ls.moveTo(*start)
    ls.drawTo(*end)
    node = ls.create()
    return NodePath(node)
