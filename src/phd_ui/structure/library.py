"""
The molecule library: geometries plus their favourite views, kept together.

Every molecule in ``_assets/molecules/`` is a structure file (source in its
title line) and may have named views in ``views.json`` next to it::

    {"methanol": {"upright": {"plane": ["C1", "O2", "H6"], "rotate": 90, "turn": -30, "tip": -20},
                  "organic": {"plane": ["C1", "O2", "H6"], "skeletal": true}}}

A view entry holds the keyword arguments of ``project`` plus an optional
``"skeletal": true`` (or a dict of ``skeletal`` arguments). :func:`view`
turns a name into a projection; :func:`save` adds a molecule or a view, so
the molecules used most are one call away, and surface species can join
the same way once they have a geometry (adsorbate plus the surface atoms
it binds to, in one file).
"""

from __future__ import annotations

import json
from pathlib import Path

from phd_ui.structure.molecule import MOLECULES_DIR, Molecule, load
from phd_ui.structure.view import Projection, project, skeletal

__all__ = ["save", "view", "views", "write_mol"]

VIEWS_FILE = MOLECULES_DIR / "views.json"
_ORDER = {"single": 1, "double": 2, "triple": 3, "partial": 4, "surface": 8}


def views(name: str | None = None) -> dict:
    """
    Stored views: all of them, or those of one molecule.

    Parameters
    ----------
    name : str, optional
        Molecule name.

    Returns
    -------
    dict
        ``{molecule: {view: arguments}}``, or ``{view: arguments}`` for one.
    """
    data = json.loads(VIEWS_FILE.read_text(encoding="utf-8")) if VIEWS_FILE.exists() else {}
    return data if name is None else data.get(name, {})


def view(name: str, which: str, **override: object) -> Projection:
    """
    A molecule from the library in one of its stored views.

    Parameters
    ----------
    name : str
        Molecule name (``'methanol'``).
    which : str
        View name (``'upright'``, ``'organic'``, ...).
    **override
        Replace any stored argument for this call (``turn=10``).

    Returns
    -------
    Projection
        Ready for ``render``, ``sketch.molecule`` or ``plotting.draw_projection``.
    """
    stored = views(name)
    if which not in stored:
        raise KeyError(f"No view '{which}' for '{name}'. Stored: {', '.join(stored) or 'none'}.")
    args = {**stored[which], **override}
    skel = args.pop("skeletal", False)
    p = project(load(name), **args)
    return skeletal(p, **(skel if isinstance(skel, dict) else {})) if skel else p


def write_mol(mol: Molecule, path: str | Path) -> Path:
    """
    Write a molecule as MOL V2000 (positions in Å, bond orders kept).

    Parameters
    ----------
    mol : Molecule
        The structure; its title goes into the first line.
    path : str or pathlib.Path
        Output file.

    Returns
    -------
    pathlib.Path
        The file.
    """
    rows = [mol.title, "  phd_ui", "", f"{len(mol.symbols):3d}{len(mol.bonds):3d}  0  0  0  0  0  0  0  0999 V2000"]
    rows += [f"{x / 100:10.4f}{y / 100:10.4f}{z / 100:10.4f} {s:<3} 0  0  0  0  0  0  0  0  0  0  0  0"
             for s, (x, y, z) in zip(mol.symbols, mol.xyz)]
    rows += [f"{i + 1:3d}{j + 1:3d}{_ORDER.get(k, 1):3d}  0" for i, j, k in mol.bonds]
    path = Path(path)
    path.write_text("\n".join(rows + ["M  END", ""]), encoding="utf-8")
    return path


def save(name: str, mol: Molecule | None = None, views_: dict | None = None, overwrite: bool = False) -> None:
    """
    Add a molecule and/or views to the library.

    Parameters
    ----------
    name : str
        Library name, also the file stem.
    mol : Molecule, optional
        Geometry to store as ``<name>.mol``. Its title must say where the
        geometry comes from; a molecule without a source is refused.
    views_ : dict, optional
        ``{view name: project arguments}`` to add or replace.
    overwrite : bool, optional
        Allow replacing an existing structure file.

    Raises
    ------
    ValueError
        For a molecule with an empty title (no source).
    FileExistsError
        If the structure exists and `overwrite` is False.
    """
    if mol is not None:
        if not mol.title.strip():
            raise ValueError("Give the molecule a title naming the source of its geometry before storing it.")
        existing = [p for p in MOLECULES_DIR.glob(f"{name}.*") if p.suffix in (".xyz", ".mol", ".sdf")]
        if existing and not overwrite:
            raise FileExistsError(f"'{name}' is already in the library ({existing[0].name}); pass overwrite=True.")
        write_mol(mol, MOLECULES_DIR / f"{name}.mol")
    if views_:
        data = views()
        data.setdefault(name, {}).update(views_)
        VIEWS_FILE.write_text(json.dumps(data, indent=1) + "\n", encoding="utf-8")
