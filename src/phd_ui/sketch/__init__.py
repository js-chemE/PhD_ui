"""
Schematic drawings as structured, regenerable SVG.

Surfaces, particles, vacancies and sites, drawn in picometres with the atom
conventions of :mod:`phd_ui.colors.atoms`, written as an SVG whose panels
are layers and whose parts are named groups. See :mod:`phd_ui.sketch.scene`
for the file layout and :mod:`phd_ui.sketch.primitives` for the building
blocks; :func:`atom_sheet` writes the element library for Illustrator.
"""

from phd_ui.sketch.scene import PANEL_PARTS, STATES, Group, Panel, Scene
from phd_ui.sketch.primitives import (
    Placed,
    angle_mark,
    arrow,
    label,
    leader,
    molecule,
    rest_y,
    site,
    slab,
    spin,
    stack,
    vacancies,
    vacancy,
)
from phd_ui.sketch.sheet import atom_sheet

__all__ = [
    "PANEL_PARTS",
    "STATES",
    "Group",
    "Panel",
    "Placed",
    "Scene",
    "angle_mark",
    "arrow",
    "atom_sheet",
    "label",
    "leader",
    "molecule",
    "rest_y",
    "site",
    "slab",
    "spin",
    "stack",
    "vacancies",
    "vacancy",
]
