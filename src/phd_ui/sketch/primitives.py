"""
Building blocks of a surface sketch: slabs, stacked particles, vacancies,
sites, labels, leader lines and arrows.

Every function draws into a :class:`~phd_ui.sketch.scene.Group` (usually a
panel part, ``panel.part('support')``), in pm, and wraps what it draws in a
named child group, so the file reads ``panel-90CuGa.particles.island-left``
rather than a flat list of circles. Functions that place atoms return a
:class:`Placed` with every position, so a vacancy, a site ring or a label
can be put on a real lattice position instead of a guessed coordinate.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field

from phd_ui.sketch.scene import Group, Scene, _num, _ns

import xml.etree.ElementTree as ET

__all__ = [
    "Placed",
    "angle_mark",
    "arrow",
    "molecule",
    "spin",
    "label",
    "leader",
    "site",
    "slab",
    "stack",
    "vacancies",
    "vacancy",
]

_SIN60: float = math.sqrt(3) / 2


@dataclass
class Placed:
    """
    Positions of the atoms one call placed.

    Attributes
    ----------
    atoms : list of tuple
        ``(symbol, x, y, row, col)`` of every drawn atom, in pm. Rows count
        from the surface (slab) or from the base (stack), columns from the
        left reference point.
    omitted : list of tuple
        ``(symbol, x, y, row, col)`` of positions left empty on purpose,
        for :func:`vacancies`.
    """

    atoms: list[tuple[str, float, float, int, int]] = field(default_factory=list)
    omitted: list[tuple[str, float, float, int, int]] = field(default_factory=list)

    def at(self, row: int, col: int) -> tuple[float, float]:
        """
        Centre of the position at (`row`, `col`), drawn or omitted.

        Parameters
        ----------
        row, col : int
            Lattice indices.

        Returns
        -------
        tuple of float
            ``(x, y)`` in pm.

        Raises
        ------
        KeyError
            If the call placed nothing there.
        """
        for symbol, x, y, r, c in self.atoms + self.omitted:
            if (r, c) == (row, col):
                return x, y
        raise KeyError(f"No position at row {row}, col {col}.")

    def nearest(self, x: float, row: int = 0, symbol: str | None = None) -> tuple[float, float]:
        """
        Centre of the drawn atom in `row` closest to `x`.

        Parameters
        ----------
        x : float
            Horizontal position, in pm.
        row : int, optional
            Row index, the surface row by default.
        symbol : str, optional
            Only atoms of this element.

        Returns
        -------
        tuple of float
            ``(x, y)`` in pm, for a leader or a site ring that should land
            on an atom near a chosen spot whatever the lattice pitch.
        """
        hits = self.row(row, symbol)
        if not hits:
            raise KeyError(f"No drawn atom in row {row}" + (f" of {symbol}" if symbol else "") + ".")
        bx, by, _ = min(hits, key=lambda h: abs(h[0] - x))
        return bx, by

    def row(self, row: int, symbol: str | None = None) -> list[tuple[float, float, int]]:
        """
        Drawn positions of one row, left to right.

        Parameters
        ----------
        row : int
            Row index; 0 is the surface row of a slab or the base of a stack.
        symbol : str, optional
            Keep only this element.

        Returns
        -------
        list of tuple
            ``(x, y, col)`` per atom.
        """
        hits = [(x, y, c) for s, x, y, r, c in self.atoms if r == row and (symbol is None or s == symbol)]
        return sorted(hits)


def _element_at(elements: Sequence[str], row: int, col: int) -> str:
    return elements[(row + col) % len(elements)]


def _states(ox: Iterable[tuple[int, int]] | str | None, rows: Sequence[int]) -> set[tuple[int, int]]:
    if ox is None:
        return set()
    if ox == "base":
        return {(0, c) for c in range(rows[0])}
    return set(ox)  # type: ignore[arg-type]


def slab(
    group: Group,
    elements: str | Sequence[str],
    x0: float,
    x1: float,
    y_top: float,
    depth: float,
    name: str | None = None,
    pitch: float | None = None,
    omit: Iterable[tuple[int, int]] = (),
) -> Placed:
    """
    A support or bulk: rows of atoms from a surface row downwards.

    One element is packed hexagonally (each row offset by half a pitch),
    two elements as a checkerboard, so an oxide shows metal and oxygen
    alternating along and across rows.

    Parameters
    ----------
    group : Group
        Where to draw, usually ``panel.part('support')``.
    elements : str or sequence of str
        ``'Cu'`` or ``('Ga', 'O')``.
    x0, x1 : float
        Horizontal extent in pm; atoms run one pitch past both ends, so a
        clipped panel shows the slab edge to edge.
    y_top : float
        Centre line of the surface row, in pm.
    depth : float
        How far down rows continue, in pm.
    name : str, optional
        Group name, by default the elements joined (``'GaO'``).
    pitch : float, optional
        Centre distance along a row. Default: touching neighbours, the sum
        of the two radii.
    omit : iterable of (row, col), optional
        Positions left empty, e.g. surface oxygen vacancies. Col 0 is the
        first atom at or right of `x0`.

    Returns
    -------
    Placed
        Drawn and omitted positions.
    """
    els = (elements,) if isinstance(elements, str) else tuple(elements)
    scene = group.scene
    radii = [scene.radius(e) for e in els]
    single = len(els) == 1
    if pitch is None:
        pitch = 2 * radii[0] if single else radii[0] + radii[1]
    row_dy = pitch * _SIN60 if single else pitch
    skip = set(omit)
    g = group.group(name or "".join(els))
    placed = Placed()
    n_rows = int(depth // row_dy) + 2
    n_cols = int((x1 - x0) // pitch) + 2
    for row in range(n_rows):
        y = y_top + row * row_dy
        offset = pitch / 2 if (single and row % 2) else 0.0
        for col in range(-1, n_cols + 1):
            x = x0 + offset + col * pitch
            symbol = els[0] if single else _element_at(els, row, col)
            if (row, col) in skip:
                placed.omitted.append((symbol, x, y, row, col))
                continue
            g.atom(symbol, x, y)
            placed.atoms.append((symbol, x, y, row, col))
    return placed


def stack(
    group: Group,
    elements: str | Sequence[str],
    x_left: float,
    y_base: float,
    rows: Sequence[int],
    name: str | None = None,
    pitch: float | None = None,
    ox: Iterable[tuple[int, int]] | str | None = None,
    omit: Iterable[tuple[int, int]] = (),
) -> Placed:
    """
    A particle or island: rows stacked upwards, a pyramid.

    One element is close packed, each row half a pitch right of the one
    below, like :func:`slab`. Two elements continue the checkerboard of an
    oxide slab: each row one pitch right of the one below, so every atom
    sits on an atom of the other element.

    Parameters
    ----------
    group : Group
        Where to draw, usually ``panel.part('particles')``.
    elements : str or sequence of str
        ``'Cu'`` for a metal particle, ``('O', 'Ga')`` for an oxide island
        starting with O at the bottom-left.
    x_left : float
        Centre of the bottom-left atom, in pm.
    y_base : float
        Centre line of the bottom row, in pm. :func:`rest_y` gives the line
        on which a row rests on a slab.
    rows : sequence of int
        Atoms per row, bottom first: ``[3, 2]`` is a three-atom base with
        two on top.
    name : str, optional
        Group name, by default the elements joined.
    pitch : float, optional
        Centre distance along a row; default touching neighbours.
    ox : iterable of (row, col) or 'base', optional
        Atoms drawn in the oxidised state; ``'base'`` is the whole bottom
        row, the atoms in contact with the support.
    omit : iterable of (row, col), optional
        Positions left empty.

    Returns
    -------
    Placed
        Drawn and omitted positions.
    """
    els = (elements,) if isinstance(elements, str) else tuple(elements)
    scene = group.scene
    radii = [scene.radius(e) for e in els]
    if pitch is None:
        pitch = 2 * radii[0] if len(els) == 1 else radii[0] + radii[1]
    single = len(els) == 1
    step, row_dy = (pitch / 2, pitch * _SIN60) if single else (pitch, pitch)
    oxidised = _states(ox, rows)
    skip = set(omit)
    g = group.group(name or "".join(els))
    placed = Placed()
    for row, count in enumerate(rows):
        y = y_base - row * row_dy
        for col in range(count):
            x = x_left + row * step + col * pitch
            # checkerboard on the absolute column, col + row, as in slab()
            symbol = els[0] if single else _element_at(els, row, col + row)
            if (row, col) in skip:
                placed.omitted.append((symbol, x, y, row, col))
                continue
            g.atom(symbol, x, y, "ox" if (row, col) in oxidised else "plain")
            placed.atoms.append((symbol, x, y, row, col))
    return placed


def rest_y(scene: Scene, support: Placed, symbol: str | Sequence[str]) -> float:
    """
    Centre line for a row sitting on the surface row of a slab.

    Parameters
    ----------
    scene : Scene
        The scene, for the drawn radii.
    support : Placed
        The slab, from :func:`slab`.
    symbol : str or sequence of str
        Element of the resting row; for a mixed row (an oxide island) its
        elements, whose mean radius is used.

    Returns
    -------
    float
        y in pm: the surface line minus the two radii projected at 60°, the
        height of an atom resting in a hollow between two surface atoms. The
        larger surface atom sets the support side.
    """
    els = (symbol,) if isinstance(symbol, str) else tuple(symbol)
    r_row = sum(scene.radius(e) for e in els) / len(els)
    top = [(s, y) for s, _, y, r, _ in support.atoms if r == 0]
    y_top = min(y for _, y in top)
    r_support = max(scene.radius(s) for s, _ in top)
    return y_top - (r_row + r_support) * _SIN60


def vacancy(group: Group, symbol: str, x: float, y: float) -> None:
    """
    An empty lattice position: a dashed ring the size of the missing atom.

    Parameters
    ----------
    group : Group
        Usually ``panel.part('defects')``.
    symbol : str
        Element that is missing; sets the ring size and its edge colour.
    x, y : float
        Centre, in pm.
    """
    scene = group.scene
    scene._vacancy_symbols.add(symbol)
    r = scene.radius(symbol) - scene.pt(0.3)
    group.add("circle", {"class": f"vacancy-{symbol}", "cx": _num(x), "cy": _num(y), "r": _num(r)})


def vacancies(group: Group, placed: Placed, name: str = "vacancies") -> None:
    """
    Draw every position a :func:`slab` or :func:`stack` call omitted.

    Parameters
    ----------
    group : Group
        Usually ``panel.part('defects')``.
    placed : Placed
        Result of the call that left the positions empty.
    name : str, optional
        Name of the child group.
    """
    if not placed.omitted:
        return
    g = group.group(name)
    for symbol, x, y, _, _ in placed.omitted:
        vacancy(g, symbol, x, y)


def site(group: Group, x: float, y: float, r: float, name: str | None = None) -> None:
    """
    Mark a site: the blue ring of the site convention.

    Parameters
    ----------
    group : Group
        Usually ``panel.part('sites')``.
    x, y : float
        Centre, in pm.
    r : float
        Ring radius, in pm; a bit over the atom's radius reads as a ring
        around it.
    name : str, optional
        Id suffix, e.g. ``'perimeter-Ga'``.
    """
    attrs = {"class": "site", "cx": _num(x), "cy": _num(y), "r": _num(r)}
    if name:
        attrs["id"] = group.scene._unique_id(f"{group.id}.{name}")
    group.add("circle", attrs)


def label(group: Group, x: float, y: float, text: str, anchor: str = "start", kind: str = "label") -> None:
    """
    A text label; see :meth:`Scene.text` for the markup.

    Parameters
    ----------
    group : Group
        Usually ``panel.part('labels')``.
    x, y : float
        Baseline anchor, in pm.
    text : str
        ``'GaO_x'``, ``'Cu^{δ+}'``, ...
    anchor : {'start', 'middle', 'end'}, optional
        Horizontal anchor.
    kind : {'label', 'title', 'note'}, optional
        Style class.
    """
    group.scene.text(group, x, y, text, kind=kind, anchor=anchor)


def leader(group: Group, start: tuple[float, float], end: tuple[float, float]) -> None:
    """
    A thin line from a label to what it names.

    Parameters
    ----------
    group : Group
        Usually ``panel.part('labels')``.
    start, end : tuple of float
        End points, in pm.
    """
    group.add("line", {"class": "leader", "x1": _num(start[0]), "y1": _num(start[1]),
                       "x2": _num(end[0]), "y2": _num(end[1])})


def arrow(group: Group, start: tuple[float, float], end: tuple[float, float], head_pt: float = 5.0) -> None:
    """
    A straight arrow with a filled head, for links between panels.

    Parameters
    ----------
    group : Group
        Usually a scene layer, ``scene.layer('arrows')``.
    start, end : tuple of float
        Tail and tip, in pm.
    head_pt : float, optional
        Head length in pt at final size.
    """
    scene = group.scene
    (x0, y0), (x1, y1) = start, end
    length = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    h = scene.pt(head_pt)
    w = h * 0.35
    bx, by = x1 - ux * h, y1 - uy * h
    g = ET.SubElement(group.element, _ns("g"), {"class": "arrow-group"})
    ET.SubElement(g, _ns("line"), {"class": "arrow", "x1": _num(x0), "y1": _num(y0),
                                   "x2": _num(bx), "y2": _num(by)})
    pts = [(x1, y1), (bx - uy * w, by + ux * w), (bx + uy * w, by - ux * w)]
    ET.SubElement(g, _ns("polygon"), {"class": "arrowhead",
                                      "points": " ".join(f"{_num(a)},{_num(b)}" for a, b in pts)})


def molecule(group: Group, projection: object, x: float = 0.0, y: float = 0.0,
             name: str = "molecule", look: object = None) -> dict[str, tuple[float, float]]:
    """
    Draw a projected molecule into the sketch.

    Parameters
    ----------
    group : Group
        Usually ``panel.part('adsorbates')`` or a scene layer.
    projection : phd_ui.structure.Projection
        From ``structure.project``, ``skeletal`` or ``spin``.
    x, y : float, optional
        Scene position of the projection's origin (its first plane atom), pm.
    name : str, optional
        Group name.
    look : phd_ui.structure.Look, optional
        Appearance of every atom and bond; default ``Look()``.

    Returns
    -------
    dict of str to (float, float)
        Scene position of every atom by label, for labels and :func:`angle_mark`.

    Notes
    -----
    Geometry and styling come from ``structure.render``; this only writes
    its circles, lines and polygons as SVG, each with its id (``C1``,
    ``C1-O2``) and explicit fill, stroke and opacity, so per-atom styling
    survives into Illustrator.
    """
    from phd_ui.structure import render

    scene = group.scene
    drawing = render(projection, look, pm_per_pt=scene.pt(1.0))
    g = group.group(name)
    for it in drawing.items:
        attrs = {"id": scene._unique_id(f"{g.id}.{it.id}")}
        if it.type == "circle":
            attrs.update({"class": f"atom-{it.element}", "cx": _num(x + it.cx), "cy": _num(y - it.cy),
                          "r": _num(it.r - scene.pt(it.stroke_width_pt) / 2), "fill": it.fill, "stroke": it.stroke,
                          "stroke-width": _num(scene.pt(it.stroke_width_pt))})
            dash = it.dash_pt
        elif it.type == "line":
            attrs.update({"class": f"bond-{it.kind}", "x1": _num(x + it.x0), "y1": _num(y - it.y0),
                          "x2": _num(x + it.x1), "y2": _num(y - it.y1), "stroke": it.color,
                          "stroke-width": _num(scene.pt(it.width_pt)), "stroke-linecap": it.cap})
            dash = it.dash_pt
        else:
            attrs.update({"class": f"bond-{it.kind}", "fill": it.fill,
                          "points": " ".join(f"{_num(x + px)},{_num(y - py)}" for px, py in it.points)})
            dash = ()
        if dash:
            attrs["stroke-dasharray"] = " ".join(_num(scene.pt(v)) for v in dash)
        if it.opacity < 1:
            attrs["opacity"] = _num(it.opacity) if it.opacity >= 0.1 else f"{it.opacity:.2f}"
        g.add(it.type, attrs)
    return {lab: (x + px, y - py) for lab, (px, py) in drawing.positions.items()}


def angle_mark(
    group: Group,
    vertex: tuple[float, float],
    a: tuple[float, float],
    b: tuple[float, float],
    text: str = "",
    radius: float | None = None,
) -> None:
    """
    An arc between two bonds at a vertex, with its value written beside it.

    Parameters
    ----------
    group : Group
        Usually ``panel.part('labels')`` or a scene layer.
    vertex, a, b : tuple of float
        Scene positions in pm (from :func:`molecule`'s return): the angle
        a-vertex-b.
    text : str, optional
        Label, e.g. ``'108.9°'``. Write the true 3D angle
        (``Molecule.angle``): a projected angle is only true when the three
        atoms lie in the drawing plane.
    radius : float, optional
        Arc radius in pm; default 0.7 of the shorter bond, outside the balls.
    """
    vx, vy = vertex
    a1 = math.atan2(a[1] - vy, a[0] - vx)
    a2 = math.atan2(b[1] - vy, b[0] - vx)
    sweep = (a2 - a1) % (2 * math.pi)
    if sweep > math.pi:
        a1, a2, sweep = a2, a1, 2 * math.pi - sweep
    r = radius or 0.7 * min(math.hypot(a[0] - vx, a[1] - vy), math.hypot(b[0] - vx, b[1] - vy))
    p1 = (vx + r * math.cos(a1), vy + r * math.sin(a1))
    p2 = (vx + r * math.cos(a1 + sweep), vy + r * math.sin(a1 + sweep))
    g = group.group("angle")
    g.add("path", {"class": "angle", "d": f"M {_num(p1[0])} {_num(p1[1])} A {_num(r)} {_num(r)} 0 0 1 {_num(p2[0])} {_num(p2[1])}"})
    if text:
        mid = a1 + sweep / 2
        tr = r + group.scene.pt(6)
        anchor = "start" if math.cos(mid) > 0.3 else ("end" if math.cos(mid) < -0.3 else "middle")
        label(g, vx + tr * math.cos(mid), vy + tr * math.sin(mid) + group.scene.pt(2.5), text, anchor=anchor, kind="note")


def spin(
    group: Group,
    frames: list,
    x: float,
    y: float,
    period_s: float = 6.0,
    name: str = "spin",
    look: object = None,
) -> None:
    """
    An animated, turning molecule: one group per frame, shown in turn by SMIL.

    The SVG stays a plain, open file that plays by itself in a browser, in
    Obsidian and in PowerPoint's SVG import of the first frame; no GIF or
    video encoder is needed. Each frame is a complete ball-and-stick drawing
    (``frame-00``, ``frame-01``, ...), so any single frame can be pulled out
    as a still.

    Parameters
    ----------
    group : Group
        Usually a scene layer.
    frames : list of phd_ui.structure.Projection
        From ``structure.spin(mol, plane=..., n=...)``.
    x, y : float
        Scene position of the molecule's origin, in pm.
    period_s : float, optional
        Seconds per full turn.
    name : str, optional
        Group name.
    look : phd_ui.structure.Look, optional
        As in :func:`molecule`.
    """
    g = group.group(name)
    n = len(frames)
    step = period_s / n
    for k, p in enumerate(frames):
        fg = g.group(f"frame-{k:02d}")
        fg.element.set("visibility", "visible" if k == 0 else "hidden")
        molecule(fg, p, x, y, name="molecule", look=look)
        ET.SubElement(fg.element, _ns("animate"), {
            "attributeName": "visibility", "values": "visible;hidden", "keyTimes": f"0;{1 / n:.6f}",
            "calcMode": "discrete", "dur": f"{period_s:g}s", "begin": f"{k * step:.4f}s",
            "repeatCount": "indefinite"})
