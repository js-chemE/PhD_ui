"""
Write the atom sheet, the element library for hand-made drawings.

Every element of ``phd_ui.colors.ATOMS`` in its plain and oxidised state,
plus the vacancy ring and the site ring, at the default sketch scale
(65 pm per mm). Open ``docs/sketch/atoms.svg`` in Illustrator and copy
atoms from it, so a drawing made by hand matches one made with
``phd_ui.sketch``. Re-run after any change to ``colors/atoms.py``.

Run from the repo root: ``uv run python example/sketch_atoms.py``.
"""

from pathlib import Path

import phd_ui.sketch as sk

OUT = Path(__file__).resolve().parents[1] / "docs" / "sketch"

if __name__ == "__main__":
    path = sk.atom_sheet().save(OUT, "atoms")
    print(f"wrote {path}")
