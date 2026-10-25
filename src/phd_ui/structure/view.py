"""
Views of a molecule: rigid rotations, then a projection onto the drawing.

A view starts from the plane of three atoms (two for a linear molecule),
which lands flat in the drawing with its true angles, and then rotates the
molecule as a rigid body. Every step is a plain rotation, so 3D lengths and
angles are kept and only the projection foreshortens. The result, a
:class:`Projection`, is pure geometry in pm (y up); how it looks is decided
later by a :class:`~phd_ui.structure.look.Look` in ``render``.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field, replace

import numpy as np

from phd_ui.structure.molecule import Molecule

__all__ = ["Projection", "project", "rotation", "skeletal", "spin"]

Axis = str | Sequence[float]
_AXES = {"x": (1.0, 0.0, 0.0), "y": (0.0, 1.0, 0.0), "z": (0.0, 0.0, 1.0)}


def rotation(axis: Axis, deg: float) -> np.ndarray:
    """
    Rotation matrix about an axis of the drawing, right-handed.

    Parameters
    ----------
    axis : {'x', 'y', 'z'} or sequence of 3 floats
        ``'x'`` points right, ``'y'`` up, ``'z'`` at the viewer; or any vector.
    deg : float
        Angle in degrees, counter-clockwise looking down the axis.

    Returns
    -------
    numpy.ndarray
        3 x 3 matrix acting on column vectors.
    """
    a = np.asarray(_AXES.get(axis, axis) if isinstance(axis, str) else axis, dtype=float)
    a = a / np.linalg.norm(a)
    k = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    t = np.radians(deg)
    return np.eye(3) + np.sin(t) * k + (1 - np.cos(t)) * k @ k


@dataclass
class Projection:
    """
    A molecule seen from one direction: 2D positions plus what drawing needs.

    Attributes
    ----------
    atoms : list of (str, float, float)
        ``(symbol, x, y)`` in pm, y up.
    labels : list of str
        Atom labels (``C1``, ``O2``, ...), for ids and per-atom styling.
    bonds : list of (int, int, str)
        As in the molecule.
    depth : numpy.ndarray
        Distance in front of the drawing plane, pm, positive towards the viewer.
    reach : float
        Largest distance of any atom from the origin atom, pm. No view
        changes it, so a depth cue normalised by it is steady in a spin.
    scale : numpy.ndarray
        Perspective factor per atom (1 in a parallel view).
    stereo : dict of (int, int) to str
        ``'wedge'`` or ``'hash'`` per ``(parent, child)``, set by :func:`skeletal`.
    """

    atoms: list[tuple[str, float, float]]
    labels: list[str]
    bonds: list[tuple[int, int, str]]
    depth: np.ndarray
    reach: float
    scale: np.ndarray
    stereo: dict[tuple[int, int], str] = field(default_factory=dict)

    @property
    def order(self) -> list[int]:
        """Atom indices back to front."""
        return [int(n) for n in np.argsort(self.depth, kind="stable")]

    def point(self, i: int) -> np.ndarray:
        """Atom i as ``(x, y, depth)`` in pm."""
        return np.array([self.atoms[i][1], self.atoms[i][2], self.depth[i]])

    def items(self, under: bool = False) -> list[tuple[str, object]]:
        """
        Atoms and bonds back to front, for a painter's drawing.

        Parameters
        ----------
        under : bool, optional
            Put every bond under both its atoms (flat ball and stick, sticks
            centre to centre), not only wedges and hashes.

        Returns
        -------
        list of tuple
            ``('atom', i)`` or ``('bond', (i, j, kind))``. Atoms go back to
            front; each bond is placed just before the nearer of its two
            atoms, so it is drawn over its farther atom and hidden under
            the nearer one. A wedge or hash (in `stereo`) goes before both,
            under both balls.
        """
        order = self.order
        rank = {a: n for n, a in enumerate(order)}
        before: dict[int, list] = {}
        for b in self.bonds:
            i, j = b[0], b[1]
            flat = under or (i, j) in self.stereo or (j, i) in self.stereo
            pick = min if flat else max
            before.setdefault(pick(i, j, key=rank.__getitem__), []).append(("bond", b))
        out: list[tuple[str, object]] = []
        for a in order:
            out += before.get(a, [])
            out.append(("atom", a))
        return out


def project(
    mol: Molecule,
    plane: Sequence[int | str],
    rotate: float = 0.0,
    turn: float = 0.0,
    tip: float = 0.0,
    rotations: Sequence[tuple[Axis, float]] = (),
    flip: bool = False,
    mirror: bool = False,
    perspective: float | None = None,
) -> Projection:
    """
    View a molecule: plane flat, then rigid rotations, then project.

    Steps, in order, each a plain rotation of the whole molecule:

    1. ``plane``: first atom at the origin, second on +x, third in the
       drawing on +y (two atoms for a linear molecule).
    2. ``flip`` (180 about x, third atom below) and ``mirror`` (180 about y,
       seen from the other side).
    3. ``rotate`` about z (in the drawing), ``turn`` about y (the vertical,
       as turning a model in the hand), ``tip`` about x (positive brings
       the top towards the viewer).
    4. ``rotations``: any further ``(axis, degrees)`` pairs, axis ``'x'``,
       ``'y'``, ``'z'`` or a vector, applied in order.

    Parameters
    ----------
    mol : Molecule
        The structure.
    plane : sequence of 2 or 3 atoms
        Indices or labels, e.g. ``("C1", "O2", "H6")``.
    rotate, turn, tip : float, optional
        Degrees.
    rotations : sequence of (axis, float), optional
        Extra rotations, for any orientation the three named ones do not
        reach in a convenient order.
    flip, mirror : bool, optional
        See step 2.
    perspective : float, optional
        Viewing distance in pm; nearer atoms drawn larger and spread wider
        by ``d / (d - depth)``. None is a parallel projection.

    Returns
    -------
    Projection
        Positions, depth and reach. Textbook views: methanol upright is
        ``plane=("C1", "O2", "H6"), rotate=90, turn=-30, tip=-20``.
    """
    idx = [mol.index(a) for a in plane]
    origin = mol.xyz[idx[0]]
    ex = mol.xyz[idx[1]] - origin
    ex = ex / np.linalg.norm(ex)
    v = mol.xyz[idx[2]] - origin if len(idx) > 2 else np.array([0.0, 0.0, 1.0] if abs(ex[2]) < 0.9 else [1.0, 0, 0])
    ey = v - (v @ ex) * ex
    if np.linalg.norm(ey) < 1e-9:
        raise ValueError("The plane atoms are collinear; pass two atoms for a linear molecule.")
    ey = ey / np.linalg.norm(ey)
    local = (mol.xyz - origin) @ np.vstack([ex, ey, np.cross(ex, ey)]).T
    steps = [("x", 180.0 if flip else 0.0), ("y", 180.0 if mirror else 0.0),
             ("z", rotate), ("y", turn), ("x", tip), *rotations]
    for axis, deg in steps:
        if deg:
            local = local @ rotation(axis, deg).T
    depth = local[:, 2].copy()
    persp = perspective / (perspective - depth) if perspective else np.ones(len(depth))
    atoms = [(s, float(x * f), float(y * f)) for s, (x, y, _), f in zip(mol.symbols, local, persp)]
    return Projection(atoms, mol.labels, list(mol.bonds), depth, float(np.linalg.norm(local, axis=1).max()), persp)


def skeletal(p: Projection, spread: float = 50.0, plane_tol: float = 10.0) -> Projection:
    """
    Organic-chemistry drawing of an exact-plane view: wedge and hash.

    Start from ``project(mol, plane=...)`` without ``turn`` or ``tip``. Bonds
    leaving the plane are marked ``'wedge'`` (towards the viewer) or
    ``'hash'`` (away); terminal atoms that project onto the same direction
    (the two out-of-plane H of a methyl) are fanned apart by `spread`
    degrees at their full 3D bond length, the one behind clockwise.

    Parameters
    ----------
    p : Projection
        Exact-plane projection.
    spread : float, optional
        Degrees between two out-of-plane bonds sharing a direction.
    plane_tol : float, optional
        Atoms within this distance of the plane, pm, count as in it.

    Returns
    -------
    Projection
        A copy with `stereo` set and the fanned atoms moved.

    Notes
    -----
    A drawing convention, not a projection: moved atoms sit where they read
    best. Atoms in the plane keep their exact positions.
    """
    xy = np.array([a[1:] for a in p.atoms])
    atoms = [list(a) for a in p.atoms]
    degree = np.bincount(np.array([b[:2] for b in p.bonds]).ravel(), minlength=len(atoms)) if p.bonds else []
    in_plane = np.abs(p.depth) < plane_tol
    stereo, kids = {}, {}
    for i, j, _ in p.bonds:
        if in_plane[i] != in_plane[j]:
            parent, child = (i, j) if in_plane[i] else (j, i)
            stereo[(parent, child)] = "wedge" if p.depth[child] > 0 else "hash"
            if degree[child] == 1:
                kids.setdefault(parent, []).append(child)
    for parent, children in kids.items():
        angle = {c: np.degrees(np.arctan2(*(xy[c] - xy[parent])[::-1])) for c in children}
        left = set(children)
        while left:
            c = left.pop()
            group = sorted([c] + [k for k in left if abs((angle[k] - angle[c] + 180) % 360 - 180) < 15],
                           key=lambda k: p.depth[k])
            left -= set(group)
            for m, k in enumerate(group):
                off = 0.0 if len(group) == 1 else (m / (len(group) - 1) - 0.5) * spread
                length = float(np.linalg.norm(p.point(k) - p.point(parent)))
                a = np.radians(angle[c] + off)
                atoms[k][1:] = xy[parent] + length * np.array([np.cos(a), np.sin(a)])
    return replace(p, atoms=[(s, float(x), float(y)) for s, x, y in atoms], stereo=stereo)


def spin(mol: Molecule, plane: Sequence[int | str], n: int = 48, about: str = "turn",
         start: float = 0.0, **view: object) -> list[Projection]:
    """
    Frames of one full rigid turn, for an animation.

    Parameters
    ----------
    mol : Molecule
        The structure; its conformation stays fixed.
    plane : sequence of atoms
        As in :func:`project`.
    n : int, optional
        Frames per turn.
    about : {'turn', 'rotate', 'tip'}, optional
        Which view angle runs through 360 degrees. ``'turn'`` spins about
        the vertical before the tip, so an axis set upright with
        ``rotate`` (C-O of methanol) stands still.
    start : float, optional
        Starting angle, degrees.
    **view
        Other :func:`project` arguments.

    Returns
    -------
    list of Projection
        One per frame.
    """
    return [project(mol, plane, **{**view, about: start + 360.0 * k / n}) for k in range(n)]
