"""
3D molecules, read from file, viewed from any direction, styled freely, drawn anywhere.

Three steps, each a separate module, each plain data in and out:

1. :mod:`~phd_ui.structure.molecule`: read XYZ / MOL / SDF (what JSmol,
   Avogadro and PubChem write) or a bundled geometry, positions in pm.
2. :mod:`~phd_ui.structure.view`: plane flat, rigid rotations, projection
   (``project``), the wedge-and-hash convention (``skeletal``), frames of a
   turn (``spin``).
3. :mod:`~phd_ui.structure.look` and :mod:`~phd_ui.structure.render`: every
   atom and bond property overridable (``Look``), resolved into circles,
   lines and polygons (``render``), which ``sketch.molecule`` writes as SVG,
   ``plotting.draw_projection`` draws with matplotlib, and
   ``frames_to_json`` hands to a web frontend.

:mod:`~phd_ui.structure.export` writes SVG, PNG, PDF (a still) and SVG,
GIF (a spin) in one call; :mod:`~phd_ui.structure.model3d` a 3D model
(``.glb``) for PowerPoint's 3D animations. :mod:`~phd_ui.structure.library` keeps the molecules used most with their
favourite views: ``view("methanol", "upright")``, ``save(...)`` to add one.
"""

from phd_ui.structure.export import export, export_spin
from phd_ui.structure.library import save, view, views, write_mol
from phd_ui.structure.look import DEPTH_CUE, AtomLook, BondLook, Look
from phd_ui.structure.model3d import export_glb
from phd_ui.structure.molecule import (BOND_TOLERANCE, Molecule, available, load, perceive_bonds, read, read_mol,
                                       read_xyz)
from phd_ui.structure.render import Circle, Drawing, Line, Polygon, frames_to_json, render
from phd_ui.structure.view import Projection, project, rotation, skeletal, spin

__all__ = [
    "AtomLook", "BOND_TOLERANCE", "BondLook", "Circle", "DEPTH_CUE", "Drawing", "Line", "Look", "Molecule",
    "Polygon", "Projection", "available", "export", "export_glb", "export_spin", "frames_to_json", "load", "perceive_bonds", "project", "read",
    "read_mol", "read_xyz", "render", "rotation", "save", "skeletal", "spin", "view", "views", "write_mol",
]
