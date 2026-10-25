"""
Turn a projection and a look into drawing primitives, the one place that decides geometry on paper.

:func:`render` returns a :class:`Drawing`: circles, lines and polygons in
painter's order, in pm with y up, every colour, width and opacity resolved.
It is plain data, so any backend draws it the same way: ``sketch.molecule``
writes SVG, ``plotting.draw_projection`` draws with matplotlib, and
``Drawing.to_dict`` / :func:`frames_to_json` hand it to the IR-bands
frontend as JSON, where a renderer only has to draw three primitive types.

Bonds end where they belong:

- a stick runs from the **centre of its nearer atom** (hidden under that
  ball) to the **surface of its farther atom in 3D**, projected (to the
  centre of an atom with opacity 0, so a bond to a hidden surface atom
  ends at the surface). It is drawn
  over the far ball, so a stick coming out of a ball towards the viewer is
  seen leaving it at the right spot, and never stops short of either ball;
- wedges and hashes (``skeletal``) run **centre to centre under both balls**,
  so they meet both discs exactly at their edges.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

from phd_ui.structure.look import Look
from phd_ui.structure.view import Projection

__all__ = ["Circle", "Drawing", "Line", "Polygon", "frames_to_json", "render"]


@dataclass
class Circle:
    """An atom. Centre and radius in pm; widths and dashes in pt."""

    id: str
    cx: float
    cy: float
    r: float
    fill: str
    stroke: str
    stroke_width_pt: float
    dash_pt: tuple[float, ...]
    opacity: float
    element: str
    type: str = "circle"


@dataclass
class Line:
    """One line of a bond. End points in pm; width and dash in pt."""

    id: str
    x0: float
    y0: float
    x1: float
    y1: float
    color: str
    width_pt: float
    dash_pt: tuple[float, ...]
    cap: str
    opacity: float
    kind: str
    type: str = "line"


@dataclass
class Polygon:
    """A filled shape (a wedge). Points in pm."""

    id: str
    points: list[tuple[float, float]]
    fill: str
    opacity: float
    kind: str
    type: str = "polygon"


@dataclass
class Drawing:
    """
    Everything to draw, back to front, plus where each atom ended up.

    Attributes
    ----------
    items : list of Circle, Line, Polygon
        In drawing order.
    positions : dict of str to (float, float)
        Atom centres by label, pm, y up (for labels and angle marks).
    radii : dict of str to float
        Drawn radius by label, pm.
    """

    items: list[Circle | Line | Polygon] = field(default_factory=list)
    positions: dict[str, tuple[float, float]] = field(default_factory=dict)
    radii: dict[str, float] = field(default_factory=dict)

    def bounds(self) -> tuple[float, float, float, float]:
        """``(xmin, ymin, xmax, ymax)`` over all atoms including their radii, pm."""
        xs = [p[0] + s * self.radii[k] for k, p in self.positions.items() for s in (-1, 1)]
        ys = [p[1] + s * self.radii[k] for k, p in self.positions.items() for s in (-1, 1)]
        return min(xs), min(ys), max(xs), max(ys)

    def to_dict(self) -> dict:
        """Plain dict for JSON: ``{'items': [...], 'positions': {...}, 'radii': {...}}``, pm, y up."""
        return {"items": [asdict(i) for i in self.items], "positions": self.positions, "radii": self.radii}


def _hash_lines(a: np.ndarray, b: np.ndarray, w0: float, w1: float, step: float):
    d = b - a
    n_vec = np.array([-d[1], d[0]]) / np.linalg.norm(d)
    n = max(3, int(np.linalg.norm(d) / step))
    for t in np.linspace(1 / n, 1, n):
        c, w = a + d * t, w0 + (w1 - w0) * t
        yield c + n_vec * w / 2, c - n_vec * w / 2


def render(p: Projection, look: Look | None = None, pm_per_pt: float = 1.0) -> Drawing:
    """
    Resolve a projection into primitives.

    Parameters
    ----------
    p : Projection
        From ``project``, ``skeletal`` or ``spin``.
    look : Look, optional
        Appearance; default ``Look()``, the atom convention.
    pm_per_pt : float, optional
        Picometres per point at final size (the drawing scale), used only
        for the geometry of wedges and hashes and the spacing of double and
        triple bonds, which are given in pt.

    Returns
    -------
    Drawing
        Primitives back to front.
    """
    look = look or Look()
    sym = [a[0] for a in p.atoms]
    xy = np.array([a[1:] for a in p.atoms])
    cue = 1 + look.depth_cue * p.depth / p.reach if p.reach > 0 else np.ones(len(sym))
    r = [look.radius(s, lab, float(f * c)) for s, lab, f, c in zip(sym, p.labels, p.scale, cue)]
    rank = {a: n for n, a in enumerate(p.order)}
    out = Drawing(positions={lab: (float(x), float(y)) for lab, (x, y) in zip(p.labels, xy)},
                  radii=dict(zip(p.labels, r)))
    for what, item in p.items(under=not look.trim):
        if what == "atom":
            i = item
            a = look.atom(sym[i], p.labels[i])
            out.items.append(Circle(p.labels[i], float(xy[i, 0]), float(xy[i, 1]), r[i], a.fill, a.edge,
                                    a.edge_width_pt, a.edge_dash_pt, a.opacity, sym[i]))
            continue
        i, j, kind = item
        bid = f"{p.labels[i]}-{p.labels[j]}"
        b = look.bond(kind, p.labels[i], p.labels[j])
        stereo = p.stereo.get((i, j)) or p.stereo.get((j, i))
        if stereo:
            parent, child = (i, j) if (i, j) in p.stereo else (j, i)
            a0, a1 = xy[parent], xy[child]
            w0, w1 = b.width_pt * pm_per_pt * 0.5, look.stereo_width_pt * pm_per_pt
            if stereo == "wedge":
                n_vec = np.array([-(a1 - a0)[1], (a1 - a0)[0]]) / np.linalg.norm(a1 - a0)
                pts = [a0 + n_vec * w0 / 2, a1 + n_vec * w1 / 2, a1 - n_vec * w1 / 2, a0 - n_vec * w0 / 2]
                out.items.append(Polygon(bid, [(float(x), float(y)) for x, y in pts], b.color, b.opacity, "wedge"))
            else:
                for k, (s0, s1) in enumerate(_hash_lines(a0, a1, w0, w1, look.hash_step_pt * pm_per_pt)):
                    out.items.append(Line(f"{bid}.{k}", *map(float, (*s0, *s1)), b.color, b.width_pt * 0.5, (),
                                          "butt", b.opacity, "hash"))
            continue
        far, near = (i, j) if rank[i] <= rank[j] else (j, i)
        start, end = p.point(far), p.point(near)
        length = float(np.linalg.norm(end - start))
        r_far = r[far] if look.atom(sym[far], p.labels[far]).opacity > 0 else 0.0   # a hidden atom: bond to its centre
        if look.trim and r_far:
            if length <= r_far:
                continue
            start = start + (end - start) / length * r_far
        s0, s1 = start[:2], end[:2]
        d = s1 - s0
        norm = float(np.linalg.norm(d))
        n_vec = np.array([-d[1], d[0]]) / norm if norm > 1e-9 else np.zeros(2)
        for k in range(b.lines):
            off = n_vec * (k - (b.lines - 1) / 2) * b.spacing_pt * pm_per_pt
            out.items.append(Line(bid if b.lines == 1 else f"{bid}.{k}", *map(float, (*(s0 + off), *(s1 + off))),
                                  b.color, b.width_pt, b.dash_pt, b.cap, b.opacity, kind))
    return out


def frames_to_json(frames: list[Projection], path: str | Path, look: Look | None = None,
                   pm_per_pt: float = 1.0, period_s: float = 6.0) -> Path:
    """
    Write an animation as JSON for a web renderer (the IR-bands frontend).

    Parameters
    ----------
    frames : list of Projection
        From ``spin``, or any sequence of views (a vibration, say).
    path : str or pathlib.Path
        Output ``.json``.
    look : Look, optional
        Appearance.
    pm_per_pt : float, optional
        As in :func:`render`.
    period_s : float, optional
        Duration of the whole sequence.

    Returns
    -------
    pathlib.Path
        The file. Layout: ``{"unit": "pm", "y": "up", "period_s": ...,
        "frames": [Drawing.to_dict(), ...]}``; each item has a ``type``
        (``circle``, ``line``, ``polygon``) and an ``id`` stable across
        frames (atom label, bond ``C1-O2``), so a renderer can tween.
    """
    data = {"unit": "pm", "y": "up", "period_s": period_s,
            "frames": [render(f, look, pm_per_pt).to_dict() for f in frames]}
    path = Path(path)
    path.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    return path
