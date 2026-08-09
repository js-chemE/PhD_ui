"""
Render the phd_ui colour scheme.

Writes the three scheme views (swatches, ramps, demo) as PNG + PDF + SVG
into ``docs/colorscheme/``. Run from anywhere:

    python example/color_scheme.py
"""

from pathlib import Path

import phd_ui
from phd_ui.colors import save_previews

phd_ui.initialize()

OUT = Path(__file__).resolve().parent.parent / "docs" / "colorscheme"
OUT.mkdir(parents=True, exist_ok=True)

save_previews(OUT, figsize_key="double", prefix="colorscheme")
print("wrote scheme previews to", OUT)
