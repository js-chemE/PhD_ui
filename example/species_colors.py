"""
Render the phd_ui species colours and check them for accessibility.

The species palette is derived from the colour scheme, with the hue encoding
each species' role on a desirability axis (green = target product, blue =
feed, purple = other product, warm = undesired, grey = inert; water gets a
literal ocean blue). This script draws the palette grouped by role under
normal, greyscale and deuteranopic vision, and prints each colour with its
role, so the mapping and its colour-blind / mono legibility are both visible.

Writes ``species_colors`` (PNG + PDF + SVG) into ``docs/colorscheme/``:

    python example/species_colors.py
"""

from pathlib import Path

import phd_ui
from phd_ui.colors import SPECIES, plot_species
from phd_ui.plotting import save_figure

phd_ui.initialize()

OUT = Path(__file__).resolve().parent.parent / "docs" / "colorscheme"
OUT.mkdir(parents=True, exist_ok=True)

# The mapping, as a quick text summary.
print(f"{'species':6s} {'hex':9s} {'role':10s} family")
for name, sp in SPECIES.items():
    print(f"{name:6s} {sp.color:9s} {sp.role:10s} {sp.family or '(literal)'}")

fig = plot_species(figsize_key="double")
save_figure(fig, OUT, "species_colors")
print("wrote species preview to", OUT)
