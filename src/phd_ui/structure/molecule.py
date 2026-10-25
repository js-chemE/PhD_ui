"""
Molecules in 3D: reading structure files, measuring, bundled geometries.

Reads the files JSmol, Jmol, Avogadro and PubChem write: **XYZ** (bonds
found from covalent radii, all single) and **MOL/SDF V2000** (bond orders
kept). Positions are stored in pm, the unit of every drawing in ``phd_ui``.
Bundled experimental geometries live in ``_assets/molecules/``, one file per
molecule with its source in the title line.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from phd_ui.colors.atoms import get_atom

__all__ = ["BOND_TOLERANCE", "Molecule", "available", "load", "perceive_bonds", "read", "read_mol", "read_xyz"]

MOLECULES_DIR = Path(__file__).resolve().parents[1] / "_assets" / "molecules"

#: Two atoms count as bonded within this factor of the sum of their covalent radii.
BOND_TOLERANCE: float = 1.2

#: MOL bond types to bond kinds of ``BOND_STYLES``: 4 (aromatic) drawn as partial, 8 ("any") used here
#: for the bond of an adsorbate to a surface atom.
_MOL_ORDER = {1: "single", 2: "double", 3: "triple", 4: "partial", 8: "surface"}


@dataclass
class Molecule:
    """
    A molecule in 3D.

    Attributes
    ----------
    symbols : list of str
        Element symbols, in file order.
    xyz : numpy.ndarray
        Positions, shape ``(n, 3)``, in pm.
    bonds : list of (int, int, str)
        ``(i, j, kind)``, kind a key of ``BOND_STYLES``.
    title : str
        Title or comment line of the file, where the source is noted.
    """

    symbols: list[str]
    xyz: np.ndarray
    bonds: list[tuple[int, int, str]] = field(default_factory=list)
    title: str = ""

    @property
    def labels(self) -> list[str]:
        """Atom labels numbered like Jmol: ``C1``, ``O2``, ``H3``, ..."""
        return [f"{s}{i + 1}" for i, s in enumerate(self.symbols)]

    def index(self, atom: int | str) -> int:
        """0-based index of an atom given as index or label (``'O2'``)."""
        if isinstance(atom, (int, np.integer)):
            return int(atom)
        try:
            return self.labels.index(atom)
        except ValueError:
            raise KeyError(f"No atom '{atom}'. Atoms: {', '.join(self.labels)}.") from None

    def _v(self, a: int | str, b: int | str) -> np.ndarray:
        return self.xyz[self.index(b)] - self.xyz[self.index(a)]

    def distance(self, a: int | str, b: int | str) -> float:
        """Distance between two atoms, in pm."""
        return float(np.linalg.norm(self._v(a, b)))

    def angle(self, a: int | str, b: int | str, c: int | str) -> float:
        """Angle a-b-c at b, in degrees."""
        u, v = self._v(b, a), self._v(b, c)
        return float(np.degrees(np.arccos(np.clip(u @ v / np.linalg.norm(u) / np.linalg.norm(v), -1, 1))))

    def dihedral(self, a: int | str, b: int | str, c: int | str, d: int | str) -> float:
        """Dihedral a-b-c-d about b-c, in degrees (-180 to 180); 180 is trans."""
        b0, b1, b2 = self._v(b, a), self._v(b, c), self._v(c, d)
        b1 = b1 / np.linalg.norm(b1)
        v, w = b0 - (b0 @ b1) * b1, b2 - (b2 @ b1) * b1
        return float(np.degrees(np.arctan2(np.cross(b1, v) @ w, v @ w)))


def _text(source: str | Path) -> str:
    if isinstance(source, str) and "\n" in source:
        return source
    return Path(source).read_text(encoding="utf-8")


def perceive_bonds(mol: Molecule, tolerance: float = BOND_TOLERANCE) -> list[tuple[int, int, str]]:
    """
    Single bonds between atoms closer than `tolerance` times their covalent radii.

    Parameters
    ----------
    mol : Molecule
        The structure.
    tolerance : float, optional
        Factor on the sum of covalent radii.

    Returns
    -------
    list of (int, int, str)
        All ``'single'``: XYZ has no bond orders; read a MOL file for them.
    """
    r = np.array([get_atom(s).radius_pm for s in mol.symbols])
    d = np.linalg.norm(mol.xyz[:, None] - mol.xyz[None], axis=-1)
    i, j = np.nonzero(np.triu(d <= tolerance * (r[:, None] + r[None]), k=1))
    return [(int(a), int(b), "single") for a, b in zip(i, j)]


def read_xyz(source: str | Path, bonds: bool = True) -> Molecule:
    """
    Read an XYZ file (count, comment, ``symbol x y z`` in Å).

    Parameters
    ----------
    source : str or pathlib.Path
        File path, or the file content itself.
    bonds : bool, optional
        Find bonds from distances.

    Returns
    -------
    Molecule
        Positions in pm.
    """
    lines = _text(source).splitlines()
    n = int(lines[0].split()[0])
    rows = [line.split() for line in lines[2:2 + n]]
    mol = Molecule([r[0].capitalize() for r in rows], np.array([[float(v) for v in r[1:4]] for r in rows]) * 100.0,
                   title=lines[1].strip() if len(lines) > 1 else "")
    if bonds:
        mol.bonds = perceive_bonds(mol)
    return mol


def read_mol(source: str | Path) -> Molecule:
    """
    Read a MOL or SDF file, V2000 (the first record of an SDF).

    Parameters
    ----------
    source : str or pathlib.Path
        File path, or the file content itself.

    Returns
    -------
    Molecule
        Positions in pm, bonds with their orders.

    Raises
    ------
    ValueError
        For V3000, which is not read.
    """
    lines = _text(source).splitlines()
    if "V3000" in lines[3]:
        raise ValueError("V3000 MOL files are not read; export as V2000 (JSmol, Avogadro and PubChem all can).")
    n_atoms, n_bonds = int(lines[3][0:3]), int(lines[3][3:6])
    atoms = lines[4:4 + n_atoms]
    xyz = np.array([[float(r[0:10]), float(r[10:20]), float(r[20:30])] for r in atoms]) * 100.0
    bonds = [(int(r[0:3]) - 1, int(r[3:6]) - 1, _MOL_ORDER.get(int(r[6:9]), "single"))
             for r in lines[4 + n_atoms:4 + n_atoms + n_bonds]]
    return Molecule([r[31:34].strip() for r in atoms], xyz, bonds, lines[0].strip())


def read(path: str | Path) -> Molecule:
    """Read ``.xyz``, ``.mol`` or ``.sdf`` by extension."""
    suffix = Path(path).suffix.lower()
    if suffix == ".xyz":
        return read_xyz(path)
    if suffix in (".mol", ".sdf"):
        return read_mol(path)
    raise ValueError(f"Cannot read '{suffix}'. Export the structure from JSmol or Avogadro as .xyz or .mol.")


def available() -> list[str]:
    """Names of the bundled molecules, for :func:`load`."""
    return sorted(p.stem for p in MOLECULES_DIR.iterdir() if p.suffix in (".xyz", ".mol", ".sdf"))


def load(name: str) -> Molecule:
    """
    A bundled molecule by name, e.g. ``'methanol'``.

    Parameters
    ----------
    name : str
        File stem in ``_assets/molecules/``.

    Returns
    -------
    Molecule
        The structure; its `title` names the source of the geometry.
    """
    for suffix in (".xyz", ".mol", ".sdf"):
        if (path := MOLECULES_DIR / f"{name}{suffix}").exists():
            return read(path)
    raise KeyError(f"No bundled molecule '{name}'. Available: {', '.join(available())}.")
