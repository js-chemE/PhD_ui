"""
Render the phd_ui colour scheme.

Writes the three scheme views (swatches, ramps, demo) as PNG + PDF + SVG
into ``docs/colorscheme/`` and mirrors them into the shared figure dump.
Run from anywhere:

    python example/color_scheme.py
"""

import shutil
from pathlib import Path

import phd_ui
from phd_ui.colors import save_previews

phd_ui.initialize()

OUT = Path(__file__).resolve().parent.parent / "docs" / "colorscheme"
OUT.mkdir(parents=True, exist_ok=True)

# Mirror everything written to docs/ into the shared figure dump.
DUMP = Path(r"C:\Users\jsommer1\OneDrive\02_Projects\[UniZeug]\2024_PhD\01_Project\[figure_dump]") / "phd_ui" / "colorscheme"
DUMP.mkdir(parents=True, exist_ok=True)

save_previews(OUT, figsize_key="double", prefix="colorscheme")
for f in OUT.glob("colorscheme_*"):
    try:
        shutil.copy2(f, DUMP / f.name)
    except PermissionError:
        print(f"  (skipped locked file: {f.name})")

print("wrote scheme previews to", OUT, "and", DUMP)
