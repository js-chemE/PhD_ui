"""
Export a molecule as a 3D model (glTF binary, ``.glb``) for PowerPoint, Blender, the web.

PowerPoint (Microsoft 365) inserts ``.glb`` as a 3D model (Insert > 3D
Models > This Device) that can be turned with the mouse and animated with
its 3D animations (Turntable, Swing, Jump & Turn) or with Morph between two
slides. Turntable spins about the model's vertical axis, so export the view
you want to spin about: ``model3d.export_glb(view("methanol", "upright"), ...)``
stands C-O upright and Turntable turns methanol about C-O.

The model is real 3D: balls are spheres at the true positions, sticks are
cylinders from centre to centre, double and triple bonds parallel
cylinders. Colours, opacity and sizes come from the same :class:`Look` as
the 2D drawings (no depth cue, which a 3D viewer does itself). Units: 1 pm
in the molecule is 0.01 model units (Å as metres), which PowerPoint scales
to the slide anyway. Pure numpy, no 3D library.
"""

from __future__ import annotations

import json
import struct
from pathlib import Path

import numpy as np

from phd_ui.structure.look import Look
from phd_ui.structure.molecule import Molecule
from phd_ui.structure.view import Projection

__all__ = ["export_glb"]

#: Stick radius of a single bond in pm at the default 1.4 pt line width.
STICK_RADIUS_PM: float = 14.0
#: Centre distance of the cylinders of a double bond, pm, at the default 2 pt spacing.
STICK_SPACING_PM: float = 34.0
_UNIT = 0.01  # model units per pm


def _sphere(n_lat: int = 18, n_lon: int = 32):
    lat = np.linspace(0, np.pi, n_lat + 1)
    lon = np.linspace(0, 2 * np.pi, n_lon + 1)
    t, p = np.meshgrid(lat, lon, indexing="ij")
    v = np.stack([np.sin(t) * np.cos(p), np.cos(t), np.sin(t) * np.sin(p)], -1).reshape(-1, 3)
    idx = []
    for i in range(n_lat):
        for j in range(n_lon):
            a, b = i * (n_lon + 1) + j, (i + 1) * (n_lon + 1) + j
            idx += [a, b, a + 1, a + 1, b, b + 1]
    return v.astype(np.float32), v.astype(np.float32), np.array(idx, dtype=np.uint16)


def _cylinder(n: int = 20):
    """Unit cylinder along +y from 0 to 1, radius 1, open ends (hidden in the balls)."""
    a = np.linspace(0, 2 * np.pi, n + 1)
    ring = np.stack([np.cos(a), np.zeros_like(a), np.sin(a)], -1)
    v = np.concatenate([ring, ring + [0, 1, 0]])
    nrm = np.concatenate([ring, ring])
    idx = []
    for j in range(n):
        b0, b1, t0, t1 = j, j + 1, j + n + 1, j + n + 2
        idx += [b0, t0, b1, b1, t0, t1]
    return v.astype(np.float32), nrm.astype(np.float32), np.array(idx, dtype=np.uint16)


def _linear(hex_colour: str) -> list[float]:
    c = np.array([int(hex_colour.lstrip("#")[k:k + 2], 16) / 255 for k in (0, 2, 4)])
    return list(np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4))


def _align_y(d: np.ndarray) -> list[float]:
    """Quaternion (x, y, z, w) turning +y onto unit vector d."""
    y = np.array([0.0, 1.0, 0.0])
    c = float(y @ d)
    if c < -0.999999:
        return [1.0, 0.0, 0.0, 0.0]
    axis = np.cross(y, d)
    q = np.array([*axis, 1.0 + c])
    return list(q / np.linalg.norm(q))


def export_glb(source: Projection | Molecule, path: str | Path, look: Look | None = None,
               name: str = "molecule") -> Path:
    """
    Write a molecule as a binary glTF model.

    Parameters
    ----------
    source : Projection or Molecule
        A view (its orientation is kept: x right, y up, z towards the
        viewer, which is glTF's own frame) or a molecule as read. Use a
        rigid view, not ``skeletal``, whose fanned atoms are not true positions.
    path : str or pathlib.Path
        Output ``.glb``.
    look : Look, optional
        Colours, opacity, radii (``ball_scale`` etc.) and bond widths;
        default ``Look()``.
    name : str, optional
        Name of the root node.

    Returns
    -------
    pathlib.Path
        The file. Nodes are named after the atom labels and bonds
        (``C1``, ``C1-O2``).
    """
    look = look or Look()
    if isinstance(source, Projection):
        if source.stereo:
            raise ValueError("A skeletal projection has atoms placed by convention; export a rigid view instead.")
        xyz = np.column_stack([[a[1] for a in source.atoms], [a[2] for a in source.atoms], source.depth])
        symbols, labels, bonds = [a[0] for a in source.atoms], source.labels, source.bonds
    else:
        xyz, symbols, labels, bonds = source.xyz, source.symbols, source.labels, source.bonds
    xyz = (xyz - xyz.mean(axis=0)) * _UNIT

    blob = bytearray()
    gltf: dict = {"asset": {"version": "2.0", "generator": "phd_ui.structure.model3d"},
                  "scene": 0, "scenes": [{"nodes": [0]}], "nodes": [{"name": name, "children": []}],
                  "meshes": [], "materials": [], "accessors": [], "bufferViews": []}

    def view(data: np.ndarray, target: int) -> int:
        while len(blob) % 4:
            blob.append(0)
        gltf["bufferViews"].append({"buffer": 0, "byteOffset": len(blob), "byteLength": data.nbytes, "target": target})
        blob.extend(data.tobytes())
        return len(gltf["bufferViews"]) - 1

    def geometry(v, nrm, idx) -> dict:
        acc = gltf["accessors"]
        acc.append({"bufferView": view(v, 34962), "componentType": 5126, "count": len(v), "type": "VEC3",
                    "min": v.min(0).tolist(), "max": v.max(0).tolist()})
        acc.append({"bufferView": view(nrm, 34962), "componentType": 5126, "count": len(nrm), "type": "VEC3"})
        acc.append({"bufferView": view(idx, 34963), "componentType": 5123, "count": len(idx), "type": "SCALAR"})
        return {"POSITION": len(acc) - 3, "NORMAL": len(acc) - 2, "indices": len(acc) - 1}

    shapes = {"sphere": geometry(*_sphere()), "cylinder": geometry(*_cylinder())}
    meshes: dict[tuple, int] = {}

    def mesh(shape: str, colour: str, opacity: float) -> int:
        key = (shape, colour, round(opacity, 3))
        if key not in meshes:
            mat = {"pbrMetallicRoughness": {"baseColorFactor": [*_linear(colour), opacity], "metallicFactor": 0.0,
                                            "roughnessFactor": 0.55}}
            if opacity < 1:
                mat["alphaMode"] = "BLEND"
            gltf["materials"].append(mat)
            g = shapes[shape]
            gltf["meshes"].append({"primitives": [{"attributes": {"POSITION": g["POSITION"], "NORMAL": g["NORMAL"]},
                                                   "indices": g["indices"], "material": len(gltf["materials"]) - 1}]})
            meshes[key] = len(gltf["meshes"]) - 1
        return meshes[key]

    def node(**kw) -> None:
        gltf["nodes"].append(kw)
        gltf["nodes"][0]["children"].append(len(gltf["nodes"]) - 1)

    for i, (s, lab) in enumerate(zip(symbols, labels)):
        a = look.atom(s, lab)
        r = look.radius(s, lab) * _UNIT
        node(name=lab, mesh=mesh("sphere", a.fill, a.opacity), translation=xyz[i].tolist(), scale=[r, r, r])
    centre = xyz.mean(axis=0)
    for i, j, kind in bonds:
        b = look.bond(kind, labels[i], labels[j])
        d = xyz[j] - xyz[i]
        length = float(np.linalg.norm(d))
        u = d / length
        side = np.cross(u, (xyz[i] + xyz[j]) / 2 - centre)       # in the plane of the bond and the molecule
        if np.linalg.norm(side) < 1e-9:
            side = np.cross(u, [0.0, 0.0, 1.0] if abs(u[2]) < 0.9 else [1.0, 0.0, 0.0])
        side = np.cross(side / np.linalg.norm(side), u)
        r = STICK_RADIUS_PM * b.width_pt / 1.4 * _UNIT
        for k in range(b.lines):
            off = side * (k - (b.lines - 1) / 2) * STICK_SPACING_PM * b.spacing_pt / 2.0 * _UNIT
            node(name=f"{labels[i]}-{labels[j]}" + (f".{k}" if b.lines > 1 else ""),
                 mesh=mesh("cylinder", b.color, b.opacity), translation=(xyz[i] + off).tolist(),
                 rotation=_align_y(u), scale=[r, length, r])

    while len(blob) % 4:
        blob.append(0)
    gltf["buffers"] = [{"byteLength": len(blob)}]
    js = json.dumps(gltf, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    path = Path(path)
    path.write_bytes(struct.pack("<III", 0x46546C67, 2, 12 + 8 + len(js) + 8 + len(blob))
                     + struct.pack("<II", len(js), 0x4E4F534A) + js
                     + struct.pack("<II", len(blob), 0x004E4942) + bytes(blob))
    return path
